import { Component, ViewChildren, QueryList, ElementRef, HostListener, AfterViewInit } from '@angular/core';
import { NgFor, NgIf, NgClass } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatMenuModule } from '@angular/material/menu';
import { TipoNotaDialogComponent, TipoNotaDialogData } from './tipo-nota-dialog.component';
import { CellContextMenuComponent, CellContextMenuData } from './cell-context-menu.component';
import { CdkDragDrop, moveItemInArray, CdkDrag, CdkDropList } from '@angular/cdk/drag-drop';
import { AuthService, MaestroResponse, MateriaAsignadaConAlumnos } from '../auth.service';

interface Alumno {
  id: number;
  nombre: string;
  apellido: string;
  notas: { [tipoNotaId: number]: number };
}

interface TipoNota {
  id: number;
  nombre: string;
  color: string;
  peso: number; // porcentaje
  orden: number;
}

interface Materia {
  id: number;
  nombre: string;
  seccion: string;
}

@Component({
  selector: 'app-notas',
  templateUrl: './notas.component.html',
  styleUrls: ['./notas.component.css'],
  standalone: true,  imports: [
    NgFor, NgIf, NgClass, FormsModule,
    MatTableModule, MatFormFieldModule, MatInputModule, MatIconModule, MatButtonModule, MatDialogModule, MatTooltipModule, MatProgressSpinnerModule, MatPaginatorModule, MatMenuModule
  ],
})
export class NotasComponent {  // Array de columnas para MatTable - se actualiza dinámicamente con los getters
  displayedColumns: string[] = [];
  
  // Datos de materias y alumnos ahora dinámicos
  materias: Materia[] = [];
  materiaSeleccionada: Materia | null = null;
  alumnos: Alumno[] = [];

  filtroAlumno = '';

  // === Ajustes Excel ===
  pageSize = 12; // filas por página
  currentPage = 0;
  minTiposNota = 5; // columnas mínimas de notas (rellena con vacías si hay menos)

  // === Celdas seleccionadas ===
  selectedCell: { row: number, col: number } | null = null;

  // --- Referencia de celda seleccionada (ej. A1, B2) ---
  selectedCellRef: string | null = null;
  selectedCellValue: string | null = null;

  // Último valor editado para efectos de feedback visual
  lastEditedCell: { alumnoId: number, tipoNotaId: number } | null = null;

  // --- Maestros y materias asignadas ---
  maestrosActivos: MaestroResponse[] = [];
  maestroSeleccionadoId: number | null = null;
  cicloSeleccionado: string = '';
  materiasAsignadas: MateriaAsignadaConAlumnos[] = [];

  // Tipos de nota (deben mantenerse como propiedad)
  tiposNota: TipoNota[] = [
    { id: 1, nombre: 'Tarea', color: 'bg-blue-200', peso: 30, orden: 1 },
    { id: 2, nombre: 'Examen', color: 'bg-red-200', peso: 70, orden: 2 },
  ];

  infoMessage: string | null = null;
  infoTimeout: any;

  private notasOriginales: { [alumnoId: number]: { [tipoNotaId: number]: number } } = {};

  constructor(private dialog: MatDialog, private auth: AuthService) {
    // Restaurar selección de maestro, ciclo y materia desde localStorage
    const maestroGuardado = localStorage.getItem('notas_maestroSeleccionadoId');
    const cicloGuardado = localStorage.getItem('notas_cicloSeleccionado');
    const materiaGuardada = localStorage.getItem('notas_materiaSeleccionadaId');
    if (maestroGuardado) {
      this.maestroSeleccionadoId = Number(maestroGuardado);
    }
    if (cicloGuardado) {
      this.cicloSeleccionado = cicloGuardado;
    }
    if (materiaGuardada) {
      // Se seleccionará tras cargar las materias
      this.materiaSeleccionada = { id: Number(materiaGuardada), nombre: '', seccion: '' };
    }
    // Inicializar displayedColumns
    this.actualizarDisplayedColumns();
    this.cargarMaestrosActivos();
    // Si hay selección previa, cargar materias y alumnos automáticamente
    if (this.maestroSeleccionadoId && this.cicloSeleccionado) {
      this.cargarMateriasYAlumnos();
    }
  }

  // Carga los maestros activos desde el servicio
  cargarMaestrosActivos() {
    const params = { activo: true, page: 1, page_size: 100 };
    this.auth.getMaestrosPaginated(params).subscribe({
      next: (resp: any) => {
        this.maestrosActivos = resp.results || [];
      }
    });
  }

  // Actualiza las columnas dinámicamente
  actualizarDisplayedColumns(): void {
    const noteCols = this.tiposNota.map(t => 'tipo_' + t.id);
    const emptyCols = this.emptyNoteCols.map((_, idx) => 'empty_col_' + idx);
    this.displayedColumns = ['rowNum', 'alumno', ...noteCols, ...emptyCols, 'total'];
  }

  // --- Filtra los alumnos según el input de búsqueda ---
  get alumnosFiltrados(): Alumno[] {
    if (!this.filtroAlumno) return this.alumnos;
    return this.alumnos.filter(a =>
      (a.nombre + ' ' + a.apellido).toLowerCase().includes(this.filtroAlumno.toLowerCase())
    );
  }
  // --- Promedio general formateado ---
  get promedioGeneralFormateado(): string {
    const promedio = this.calcularPromedioGeneral();
    return promedio.toFixed(1);
  }
  
  // --- Total de páginas para la paginación ---
  get totalPages(): number {
    return Math.ceil(this.alumnosFiltrados.length / this.pageSize) || 1;
  }

  // --- Calcula el promedio general de todos los alumnos ---
  calcularPromedioGeneral(): number {
    if (this.alumnosFiltrados.length === 0) return 0;
    
    const sumaTotal = this.alumnosFiltrados.reduce((suma, alumno) => 
      suma + this.calcularTotal(alumno), 0);
    
    return sumaTotal / this.alumnosFiltrados.length;
  }

  // --- Devuelve SOLO los alumnos de la página actual ---
  get alumnosFiltradosPaginados(): Alumno[] {
    const start = this.currentPage * this.pageSize;
    return this.alumnosFiltrados.slice(start, start + this.pageSize);
  }

  // --- Calcula las filas vacías para cuadrar la tabla (Excel style) ---
  get emptyRows(): any[] {
    return Array(this.pageSize - this.alumnosFiltradosPaginados.length).fill(0);
  }

  // --- Calcula las columnas vacías si faltan tipos de nota ---
  get emptyNoteCols(): any[] {
    return Array(this.minTiposNota - this.tiposNota.length > 0 ? this.minTiposNota - this.tiposNota.length : 0).fill(0);
  }

  // --- Selecciona una celda para editar ---
  seleccionarCelda(rowIndex: number, colIndex: number, alumno?: Alumno, tipoNota?: TipoNota): void {
    const colLetter = this.getColumnLetter(colIndex);
    this.selectedCellRef = `${colLetter}${rowIndex + 1}`;
    
    if (alumno && tipoNota) {
      this.selectedCellValue = alumno.notas[tipoNota.id]?.toString() || '';
    }
    
    this.selectedCell = { row: rowIndex, col: colIndex };
  }
  
  // --- Genera letras de columnas estilo Excel (A, B, C, ..., Z, AA, AB, ...) ---
  getColumnLetter(index: number): string {
    let columnName = '';
    while (index > 0) {
      const modulo = (index - 1) % 26;
      columnName = String.fromCharCode(65 + modulo) + columnName;
      index = Math.floor((index - modulo) / 26);
    }
    return columnName;
  }
  
  // --- Maneja el focus en los inputs ---
  onInputFocus(event: Event): void {
    const inputElement = event.target as HTMLInputElement;
    if (inputElement) {
      inputElement.select();
    }
  }

  // --- Calcula el total ponderado de un alumno ---
  calcularTotal(alumno: Alumno): number {
    let total = 0;
    let sumaPesos = 0;
    for (const tipo of this.tiposNota) {
      const nota = alumno.notas[tipo.id] || 0;
      total += nota * (tipo.peso / 100);
      sumaPesos += tipo.peso;
    }
    // Si los pesos no suman 100, ajusta proporcionalmente
    return sumaPesos ? Math.round((total * 100) / sumaPesos) : 0;
  }

  // --- Selecciona materia (carga alumnos y tipos de nota reales) ---
  seleccionarMateria(materia: Materia) {
    this.materiaSeleccionada = materia;
    // Guardar selección en localStorage
    localStorage.setItem('notas_materiaSeleccionadaId', materia.id.toString());
    // Buscar la materiaAsignada correspondiente
    const matAsig = this.materiasAsignadas.find(m => m.id === materia.id);
    if (matAsig) {
      // Mapear alumnos del backend a la interfaz Alumno
      this.alumnos = (matAsig.alumnos || []).map(a => ({
        id: a.id,
        nombre: a.persona?.nombre || '',
        apellido: ((a.persona?.apellido_paterno || '') + (a.persona?.apellido_materno ? ' ' + a.persona.apellido_materno : '')).trim(),
        notas: {}
      }));
      // Cargar tipos de nota reales desde el backend
      this.auth.getTiposNotaPorMateriaAsignada(matAsig.id).subscribe({
        next: (tipos: any[]) => {
          this.tiposNota = (tipos || []).sort((a, b) => a.orden - b.orden).map(t => ({
            id: t.id,
            nombre: t.nombre,
            color: 'bg-blue-200',
            peso: t.peso,
            orden: t.orden
          }));
          this.actualizarDisplayedColumns();
          // Cargar notas reales desde el backend
          this.auth.getNotasPorMateriaAsignada(matAsig.id).subscribe({
            next: (notas: any[]) => {
              // Mapear las notas a los alumnos
              for (const nota of notas) {
                const alumno = this.alumnos.find(a => a.id === nota.alumno);
                if (alumno) {
                  alumno.notas[nota.tipo_nota] = nota.calificacion;
                }
              }
              // Inicializa notasOriginales con los valores reales
              this.notasOriginales = {};
              for (const alumno of this.alumnos) {
                this.notasOriginales[alumno.id] = {};
                for (const tipo of this.tiposNota) {
                  this.notasOriginales[alumno.id][tipo.id] = alumno.notas[tipo.id] ?? null;
                }
              }
            }
          });
        }
      });
    } else {
      this.alumnos = [];
      this.tiposNota = [];
      this.actualizarDisplayedColumns();
    }
    this.currentPage = 0;
  }

  // --- Al editar una nota ---
  editarNota(alumno: Alumno, tipoNota: TipoNota, valor: number) {
    if (valor < 0) valor = 0;
    if (valor > 100) valor = 100;
    alumno.notas[tipoNota.id] = valor;
    
    // Guardamos la celda como último editada para efectos visuales
    this.lastEditedCell = { alumnoId: alumno.id, tipoNotaId: tipoNota.id };
    
    // Aquí se haría el autosave a la API
  }

  // --- Abre el diálogo para crear/editar tipo de nota ---
  showInfoMessage(msg: string) {
    this.infoMessage = msg;
    if (this.infoTimeout) clearTimeout(this.infoTimeout);
    this.infoTimeout = setTimeout(() => {
      this.infoMessage = null;
    }, 3000);
  }

  abrirDialogoTipoNota(tipo?: TipoNota) {
    const materiaAsignadaId = this.materiaSeleccionada?.id;
    const dialogRef = this.dialog.open(TipoNotaDialogComponent, {
      width: '450px',
      panelClass: 'custom-dialog-container',
      data: tipo
        ? { nombre: tipo.nombre, peso: tipo.peso, nivel: tipo.orden, color: tipo.color, isEdit: true } as TipoNotaDialogData
        : { nombre: '', peso: 0, nivel: this.tiposNota.length + 1, color: 'bg-blue-200', isEdit: false } as TipoNotaDialogData,
    });
    dialogRef.afterClosed().subscribe((result: TipoNotaDialogData | undefined) => {
      if (result) {
        if (tipo) {
          // Editar tipo existente (solo frontend por ahora)
          tipo.nombre = result.nombre;
          tipo.peso = result.peso;
          tipo.orden = result.nivel;
          tipo.color = result.color || 'bg-blue-200';
        } else if (materiaAsignadaId) {
          // Crear nuevo tipo de nota y enviarlo al backend
          const payload = {
            nombre: result.nombre,
            peso: result.peso,
            orden: result.nivel,
            materia_asignada: materiaAsignadaId
          };
          this.auth.crearTipoNota(payload).subscribe({
            next: (resp: any) => {
              // Añadir al frontend (puedes recargar tiposNota si lo deseas)
              this.tiposNota.push({
                id: resp.id,
                nombre: resp.nombre,
                color: result.color || 'bg-blue-200',
                peso: resp.peso,
                orden: resp.orden
              });
              this.actualizarDisplayedColumns();
              if (resp.info) {
                this.showInfoMessage(resp.info); // Mostrar mensaje informativo en barra superior
              }
            }
          });
        }
      }
    });
  }

  editarTipoNota(tipo: TipoNota) {
    this.abrirDialogoTipoNota(tipo);
  }

  // --- Cambia de página ---
  onPageChange(event: any) {
    this.currentPage = event.pageIndex;
  }
  // --- Aplica una fórmula o valor desde la barra de fórmulas ---
  aplicarFormula(event: Event): void {
    const input = event.target as HTMLInputElement;
    const valor = input.value;
    
    // Aquí podríamos implementar un mini-parser de fórmulas tipo Excel
    if (this.selectedCell && this.selectedCellRef) {
      // Por ahora solo maneja valores simples, no fórmulas
      const numValue = parseFloat(valor);
      if (!isNaN(numValue)) {
        // Encuentra el alumno y tipo de nota basado en la celda seleccionada
        const rowIndex = this.selectedCell.row;
        const colIndex = this.selectedCell.col;
        
        // Este es un ejemplo simplificado, necesitarías mapear correctamente
        // la selección de celda al alumno y tipo de nota correspondientes
        if (rowIndex < this.alumnosFiltradosPaginados.length && colIndex > 1) {
          const alumno = this.alumnosFiltradosPaginados[rowIndex];
          const tipoId = colIndex - 1; // Ajusta según tu estructura de tabla
          
          if (alumno && tipoId > 0 && tipoId <= this.tiposNota.length) {
            const tipo = this.tiposNota[tipoId - 1];
            this.editarNota(alumno, tipo, numValue);
          }
        }
      }
    }
  }

  // Comprueba si una celda es la última que se editó
  isLastEditedCell(alumnoId: number, tipoNotaId: number): boolean {
    return this.lastEditedCell?.alumnoId === alumnoId && 
           this.lastEditedCell?.tipoNotaId === tipoNotaId;
  }

  // Obtiene el índice de columna para un tipo de nota
  getColumnIndexForTipo(tipo: TipoNota): number {
    // La columna de alumno está en el índice 1 (después de rowNum en 0)
    return this.tiposNota.findIndex(t => t.id === tipo.id) + 2;
  }
  // --- Selecciona una celda a partir de un alumno y un tipo de nota ---
  seleccionarCeldaAlumno(alumno: Alumno, tipoNota: TipoNota): void {
    const rowIndex = this.alumnosFiltradosPaginados.findIndex(a => a.id === alumno.id);
    if (rowIndex === -1) return; // No debería suceder
    
    const colIndex = this.getColumnIndexForTipo(tipoNota);
    this.seleccionarCelda(rowIndex, colIndex, alumno, tipoNota);
  }

  cargarMateriasYAlumnos() {
    if (this.maestroSeleccionadoId && this.cicloSeleccionado) {
      this.auth.getMateriasAsignadasPorMaestro(this.maestroSeleccionadoId, this.cicloSeleccionado).subscribe({
        next: (materias: MateriaAsignadaConAlumnos[]) => {
          this.materiasAsignadas = materias;
          // Mapear materiasAsignadas a Materia[] para el selector
          this.materias = materias.map(m => ({
            id: m.id,
            nombre: m.materia.nombre,
            seccion: m.seccion_grado.nombre
          }));
          // Seleccionar la materia guardada si existe, si no la primera
          const materiaGuardada = localStorage.getItem('notas_materiaSeleccionadaId');
          let materiaASeleccionar: Materia | null = null;
          if (materiaGuardada) {
            const idGuardado = Number(materiaGuardada);
            materiaASeleccionar = this.materias.find(m => m.id === idGuardado) || null;
          }
          if (materiaASeleccionar) {
            this.seleccionarMateria(materiaASeleccionar);
          } else if (this.materias.length > 0) {
            this.seleccionarMateria(this.materias[0]);
          } else {
            this.materiaSeleccionada = null;
            this.alumnos = [];
          }
          this.currentPage = 0;
        }
      });
    } else {
      this.materiasAsignadas = [];
      this.materias = [];
      this.materiaSeleccionada = null;
      this.alumnos = [];
      this.currentPage = 0;
    }
  }

  // --- Cuando el usuario selecciona un maestro ---
  onMaestroSeleccionado(maestroId: number) {
    this.maestroSeleccionadoId = maestroId;
    localStorage.setItem('notas_maestroSeleccionadoId', maestroId.toString());
    this.cargarMateriasYAlumnos();
  }
  // --- Cuando el usuario selecciona un ciclo ---
  onCicloSeleccionado(ciclo: string) {
    this.cicloSeleccionado = ciclo;
    localStorage.setItem('notas_cicloSeleccionado', ciclo);
    this.cargarMateriasYAlumnos();
  }

  guardarNotas() {
    if (!this.materiaSeleccionada) return;
    const notas: any[] = [];
    for (const alumno of this.alumnos) {
      for (const tipo of this.tiposNota) {
        const calificacion = alumno.notas[tipo.id];
        const original = this.notasOriginales[alumno.id]?.[tipo.id];
        if (
          (calificacion !== undefined && calificacion !== null) &&
          (original === undefined || original === null || Number(calificacion) !== Number(original))
        ) {
          notas.push({
            alumno: alumno.id,
            tipo_nota: tipo.id,
            materia_asignada: this.materiaSeleccionada.id,
            calificacion: Number(calificacion)
          });
        }
      }
    }
    if (notas.length === 0) {
      this.showInfoMessage('No hay cambios para guardar.');
      return;
    }
    this.auth.bulkUpsertNotas(notas).subscribe({
      next: (resp) => {
        this.showInfoMessage('¡Notas guardadas correctamente!');
        // Actualiza las notas originales para el próximo guardado
        for (const n of notas) {
          if (!this.notasOriginales[n.alumno]) this.notasOriginales[n.alumno] = {};
          this.notasOriginales[n.alumno][n.tipo_nota] = n.calificacion;
        }
      },
      error: (err) => {
        this.showInfoMessage('Error al guardar notas. Intenta de nuevo.');
      }
    });
  }
}
