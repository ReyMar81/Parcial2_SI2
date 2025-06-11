import { Component } from '@angular/core';
import { NgFor, NgIf, NgClass } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule } from '@angular/material/paginator';
import { AuthService } from '../../auth.service';

interface AlumnoParticipacion {
  id: number;
  nombre: string;
  apellido: string;
  puntaje?: number | null;
  observacion?: string | null;
}

interface Materia {
  id: number;
  nombre: string;
  seccion: string;
}

@Component({
  selector: 'app-participacion',
  templateUrl: './participacion.component.html',
  styleUrls: ['./participacion.component.css'],
  standalone: true,
  imports: [NgFor, NgIf, NgClass, FormsModule, MatTableModule, MatFormFieldModule, MatInputModule, MatIconModule, MatButtonModule, MatPaginatorModule],
})
export class ParticipacionComponent {
  displayedColumns: string[] = ['rowNum', 'alumno', 'puntaje', 'observacion'];
  materias: Materia[] = [];
  materiaSeleccionada: Materia | null = null;
  alumnos: AlumnoParticipacion[] = [];
  filtroAlumno = '';

  // --- Paginación ---
  currentPage = 0;
  pageSize = 15;
  get totalPages(): number {
    return Math.ceil(this.alumnosFiltrados.length / this.pageSize) || 1;
  }
  get alumnosFiltradosPaginados(): AlumnoParticipacion[] {
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

  // --- Paginación de materias (barra superior) ---
  materiasPageSize = 5;
  materiasCurrentPage = 0;
  get totalMateriasPages(): number {
    return Math.ceil(this.materias.length / this.materiasPageSize) || 1;
  }
  get materiasPaginadas(): Materia[] {
    const start = this.materiasCurrentPage * this.materiasPageSize;
    return this.materias.slice(start, start + this.materiasPageSize);
  }
  onMateriasPageChange(delta: number) {
    const next = this.materiasCurrentPage + delta;
    if (next >= 0 && next < this.totalMateriasPages) {
      this.materiasCurrentPage = next;
    }
  }

  // --- Maestros y materias asignadas ---
  maestrosActivos: any[] = [];
  maestroSeleccionadoId: number | null = null;
  cicloSeleccionado: string = '';
  materiasAsignadas: any[] = [];

  infoMessage: string | null = null;
  infoTimeout: any;

  fechaSeleccionada: string = '';

  constructor(private auth: AuthService) {
    const hoy = new Date();
    this.fechaSeleccionada = hoy.toISOString().slice(0, 10);
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
      this.materiaSeleccionada = { id: Number(materiaGuardada), nombre: '', seccion: '' };
    }
    this.cargarMaestrosActivos();
    if (this.maestroSeleccionadoId && this.cicloSeleccionado) {
      this.cargarMateriasYAlumnos();
    }
  }

  cargarMaestrosActivos() {
    const params = { activo: true, page: 1, page_size: 100 };
    this.auth.getMaestrosPaginated(params).subscribe({
      next: (resp: any) => {
        this.maestrosActivos = resp.results || [];
      }
    });
  }

  get alumnosFiltrados(): AlumnoParticipacion[] {
    if (!this.filtroAlumno) return this.alumnos;
    return this.alumnos.filter(a =>
      (a.nombre + ' ' + a.apellido).toLowerCase().includes(this.filtroAlumno.toLowerCase())
    );
  }

  seleccionarMateria(materia: Materia) {
    this.materiaSeleccionada = materia;
    localStorage.setItem('notas_materiaSeleccionadaId', materia.id.toString());
    const matAsig = this.materiasAsignadas.find((m: any) => m.id === materia.id);
    if (matAsig && Array.isArray(matAsig.alumnos)) {
      this.alumnos = matAsig.alumnos.map((a: any) => ({
        id: a.id,
        nombre: a.persona?.nombre || '',
        apellido: ((a.persona?.apellido_paterno || '') + (a.persona?.apellido_materno ? ' ' + a.persona.apellido_materno : '')).trim(),
        puntaje: null,
        observacion: ''
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
          if (this.materias.length > 0) {
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

  cargarParticipacionesPorFecha() {
    if (!this.materiaSeleccionada || !this.fechaSeleccionada) return;
    this.auth.getParticipacionesPorMateriaYFecha(this.materiaSeleccionada.id, this.fechaSeleccionada).subscribe({
      next: (participaciones: any[]) => {
        for (const alumno of this.alumnos) {
          const part = participaciones.find(p => p.alumno === alumno.id);
          alumno.puntaje = part ? part.puntaje : null;
          alumno.observacion = part ? part.observacion : '';
        }
      },
      error: () => {
        for (const alumno of this.alumnos) {
          alumno.puntaje = null;
          alumno.observacion = '';
        }
      }
    });
  }

  guardarParticipaciones() {
    if (!this.materiaSeleccionada || !this.fechaSeleccionada) {
      this.showInfoMessage('Selecciona materia y fecha.');
      return;
    }
    const participaciones = this.alumnos
      .filter(a => a.puntaje !== null && a.puntaje !== undefined)
      .map(a => ({
        alumno: a.id,
        materia_asignada: this.materiaSeleccionada!.id,
        fecha: this.fechaSeleccionada,
        puntaje: a.puntaje,
        observacion: a.observacion || ''
      }));
    this.auth.bulkUpsertParticipaciones(participaciones).subscribe({
      next: () => this.showInfoMessage('Participaciones guardadas.'),
      error: () => this.showInfoMessage('Error al guardar participaciones.')
    });
  }

  showInfoMessage(msg: string) {
    this.infoMessage = msg;
    if (this.infoTimeout) clearTimeout(this.infoTimeout);
    this.infoTimeout = setTimeout(() => {
      this.infoMessage = null;
    }, 2500);
  }
}
