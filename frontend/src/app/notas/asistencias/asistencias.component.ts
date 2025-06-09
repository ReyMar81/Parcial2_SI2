import { Component } from '@angular/core';
import { NgFor, NgIf, NgClass } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../../auth.service';

interface Alumno {
  id: number;
  nombre: string;
  apellido: string;
  asistencia?: string | null;
}

interface Materia {
  id: number;
  nombre: string;
  seccion: string;
}

@Component({
  selector: 'app-asistencias',
  templateUrl: './asistencias.component.html',
  styleUrls: ['./asistencias.component.css'],
  standalone: true,  imports: [
    NgFor, NgIf, NgClass, FormsModule,
    MatTableModule, MatFormFieldModule, MatInputModule, MatIconModule, MatButtonModule
  ],
})
export class AsistenciasComponent {
  displayedColumns: string[] = ['rowNum', 'alumno', 'presente', 'ausente', 'licencia'];
  materias: Materia[] = [];
  materiaSeleccionada: Materia | null = null;
  alumnos: Alumno[] = [];
  filtroAlumno = '';

  // --- Paginación ---
  currentPage = 0;
  pageSize = 15;
  get totalPages(): number {
    return Math.ceil(this.alumnosFiltrados.length / this.pageSize) || 1;
  }
  get alumnosFiltradosPaginados(): Alumno[] {
    const start = this.currentPage * this.pageSize;
    return this.alumnosFiltrados.slice(start, start + this.pageSize);
  }
  get emptyRows(): any[] {
    return Array(this.pageSize - this.alumnosFiltradosPaginados.length).fill(0);
  }
  onPageChange(event: any) {
    if (event && typeof event.pageIndex === 'number') {
      this.currentPage = event.pageIndex;
    } else if (event && event.pageIndex !== undefined) {
      this.currentPage = event.pageIndex;
    } else if (typeof event === 'object' && 'pageIndex' in event) {
      this.currentPage = event.pageIndex;
    } else if (typeof event === 'number') {
      this.currentPage = event;
    }
  }

  // --- Maestros y materias asignadas ---
  maestrosActivos: any[] = [];
  maestroSeleccionadoId: number | null = null;
  cicloSeleccionado: string = '';
  materiasAsignadas: any[] = [];

  // Mensaje de información para el usuario
  infoMessage: string | null = null;
  infoTimeout: any;

  // Nueva propiedad para la fecha seleccionada
  fechaSeleccionada: string = '';

  constructor(private auth: AuthService) {
    // Inicializar fechaSeleccionada con la fecha de hoy
    const hoy = new Date();
    this.fechaSeleccionada = hoy.toISOString().slice(0, 10);
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

  // --- Filtra los alumnos según el input de búsqueda ---
  get alumnosFiltrados(): Alumno[] {
    if (!this.filtroAlumno) return this.alumnos;
    return this.alumnos.filter(a =>
      (a.nombre + ' ' + a.apellido).toLowerCase().includes(this.filtroAlumno.toLowerCase())
    );
  }

  // --- Selecciona materia (carga alumnos) ---
  seleccionarMateria(materia: Materia) {
    this.materiaSeleccionada = materia;
    localStorage.setItem('notas_materiaSeleccionadaId', materia.id.toString());
    const matAsig = this.materiasAsignadas.find((m: any) => m.id === materia.id);
    if (matAsig && Array.isArray(matAsig.alumnos)) {
      this.alumnos = matAsig.alumnos.map((a: any) => ({
        id: a.id,
        nombre: a.persona?.nombre || '',
        apellido: ((a.persona?.apellido_paterno || '') + (a.persona?.apellido_materno ? ' ' + a.persona.apellido_materno : '')).trim(),
      }));
    } else {
      this.alumnos = [];
    }
  }

  cargarMateriasYAlumnos() {
    if (this.maestroSeleccionadoId && this.cicloSeleccionado) {
      this.auth.getMateriasAsignadasPorMaestro(this.maestroSeleccionadoId, this.cicloSeleccionado).subscribe({
        next: (materias: any[]) => {
          this.materiasAsignadas = materias;
          this.materias = materias.map(m => ({
            id: m.id,
            nombre: m.materia.nombre,
            seccion: m.seccion_grado.nombre
          }));
          const materiaGuardada = localStorage.getItem('notas_materiaSeleccionadaId');
          let materiaASeleccionar: any = null;
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
        }
      });
    } else {
      this.materiasAsignadas = [];
      this.materias = [];
      this.materiaSeleccionada = null;
      this.alumnos = [];
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

  // --- Marcar asistencia (Presente, Ausente, Licencia) ---
  marcarAsistencia(alumno: any, estado: 'P' | 'A' | 'L') {
    alumno.asistencia = estado;
  }

  // Cargar asistencias para la materia y fecha seleccionada
  cargarAsistenciasPorFecha() {
    if (!this.materiaSeleccionada || !this.fechaSeleccionada) return;
    this.auth.getAsistenciasPorMateriaYFecha(this.materiaSeleccionada.id, this.fechaSeleccionada).subscribe({
      next: (asistencias: any[]) => {
        // Mapear asistencias a los alumnos
        const mapEstadoBackend = (estado: string) => {
          if (estado === 'presente') return 'P';
          if (estado === 'ausente') return 'A';
          if (estado === 'justificado') return 'L';
          return null;
        };
        for (const alumno of this.alumnos) {
          const asistencia = asistencias.find(a => a.alumno === alumno.id);
          alumno.asistencia = asistencia ? mapEstadoBackend(asistencia.estado) : null;
        }
      },
      error: () => {
        for (const alumno of this.alumnos) {
          alumno.asistencia = null;
        }
      }
    });
  }

  // Guardar asistencias en bulk (upsert)
  guardarAsistencias() {
    if (!this.materiaSeleccionada || !this.fechaSeleccionada) {
      this.showInfoMessage('Selecciona materia y fecha.');
      return;
    }
    // Solo enviar asistencias válidas (A, P, L)
    const estadosValidos = ['A', 'P', 'L'];
    // Mapear los valores de asistencia a los que espera el backend
    const mapEstado = (estado: string) => {
      if (estado === 'P') return 'presente';
      if (estado === 'A') return 'ausente';
      if (estado === 'L') return 'justificado';
      return estado;
    };
    const asistencias = this.alumnos
      .filter(a => estadosValidos.includes(a.asistencia as string))
      .map(a => ({
        alumno: a.id,
        materia_asignada: this.materiaSeleccionada!.id,
        fecha: this.fechaSeleccionada,
        estado: mapEstado(a.asistencia as string)
      }));
    if (asistencias.length === 0) {
      this.showInfoMessage('No hay asistencias para guardar.');
      return;
    }
    this.auth.bulkUpsertAsistencias(asistencias).subscribe({
      next: (resp: any) => {
        this.showInfoMessage('¡Asistencias guardadas correctamente!');
        this.cargarAsistenciasPorFecha();
      },
      error: (err: any) => {
        this.showInfoMessage('Error al guardar asistencias.');
      }
    });
  }

  showInfoMessage(msg: string) {
    this.infoMessage = msg;
    if (this.infoTimeout) {
      clearTimeout(this.infoTimeout);
    }
    this.infoTimeout = setTimeout(() => {
      this.infoMessage = null;
    }, 3000);
  }
}
