import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';

// ---- Interfaces ----

// Materia
export interface Materia {
  id?: number;
  nombre: string;
  descripcion: string;
  activo: boolean; // <-- Agregado para reflejar el backend
}

// Grado
export interface Grado {
  id?: number;
  nombre: string;
  nivel?: string;
  descripcion?: string;
  activo: boolean; // <-- Agregado para reflejar el backend
}

// Seccion
export interface Seccion {
  id?: number;
  nombre: string;
  activo: boolean;
}

// Maestro (Petición)
export interface MaestroCreate{
  persona: {
    id?: number;
    nombre: string;
    apellido_paterno: string;
    apellido_materno: string;
    genero: 'M' | 'F';
    ci: string;
    direccion: string;
    contacto: string;
    fecha_nacimiento: string;
  };
  especialidad: string;
}
export interface MaestroCreateResponse {
  mensaje: string;
  maestro: {
    registro: string;
    username: string;
    password: string;
  };
}
// Maestro (Respuesta)
export interface MaestroResponse {
  id: number;
  persona: PersonaResponse;
  registro: string;
  especialidad: string;
}
export interface PersonaResponse {
  id: number;
  usuario: number;
  nombre: string;
  apellido_paterno: string;
  apellido_materno: string;
  genero: string;
  ci: string;
  direccion: string;
  contacto: string;
  fecha_nacimiento: string;
}

// Alumnos (Petición)
export interface AlumnoCreate{
  persona: {
    id?: number;
    nombre: string;
    apellido_paterno: string;
    apellido_materno: string;
    genero: 'M' | 'F';
    ci: string;
    direccion: string;
    contacto: string;
    fecha_nacimiento: string;
  };
  registro: string;
}
export interface AlumnoResponse {
  id: number;
  persona: PersonaResponse;
  registro: string;
}

// Alumnos (Respuesta)
export interface AlumnoResponse {
  id: number;
  persona: PersonaResponse;
  registro: string;
}

export interface PersonaResponse {
  id: number;
  usuario: number;
  nombre: string;
  apellido_paterno: string;
  apellido_materno: string;
  genero: string;
  ci: string;
  direccion: string;
  contacto: string;
  fecha_nacimiento: string;
}
// Perfil
export interface PerfilResponse {
  id: number;
  username: string;
  is_superuser: boolean;
  privilegios: string[];
  roles: string[];
}

// Inscripcion (Petición)
export interface InscripcionRequest {
  alumno: {
    nombre: string;
    apellido_paterno: string;
    apellido_materno: string;
    genero: string;
    ci: string;
    direccion: string;
    contacto: string;
    fecha_nacimiento: string;
  };
  tutor?: {
    nombre: string;
    apellido_paterno: string;
    apellido_materno: string;
    genero: string;
    ci: string;
    direccion: string;
    contacto: string;
    fecha_nacimiento: string;
    ocupacion: string;
  };
  tutor_existente_ci?: string;
  tipo_relacion: string;
  seccion_grado_id: number;
  ciclo: string;
}

// Inscripcion (Respuesta)
export interface InscripcionUsuarioResponse {
  username: string;
  password: string;
}
export interface InscripcionResponse {
  mensaje: string;
  alumno: InscripcionUsuarioResponse;
  tutor: InscripcionUsuarioResponse;
}

// Tutor (Petición)
export interface TutorCreate {
  persona: {
    id?: number;
    nombre: string;
    apellido_paterno: string;
    apellido_materno: string;
    genero: 'M' | 'F';
    ci: string;
    direccion: string;
    contacto: string;
    fecha_nacimiento: string;
  };
  ocupacion: string;
  alumno_id?: number; // Permitir asociar alumno existente al crear tutor
}
export interface TutorCreateResponse {
  mensaje: string;
  tutor: {
    username: string;
    password: string;
  };
}
// Tutor (Respuesta)
export interface TutorResponse {
  id: number;
  persona: PersonaResponse;
  ocupacion: string;
  alumnos_asociados?: AlumnoResponse[];
  registro?: string;
}

// SeccionGrado (Asignaciones)
export interface SeccionGrado {
  id?: number;
  aula: string;
  capacidad_maxima: number;
  activo: boolean;
  seccion_id: number;
  grado_id: number;
  seccion_nombre?: string;
  grado_nombre?: string;
  nombre?: string;
}

// MateriaAsignada (Asignación de Materias)
export interface MateriaAsignada {
  id?: number;
  ciclo: string;
  materia: number | { id: number; nombre: string };
  maestro: number | { id: number; nombre: string };
  seccion_grado: number | { id: number; nombre: string };
  horas_semanales: number;
}

// --- MateriaAsignada con alumnos ---
export interface MateriaAsignadaConAlumnos {
  id: number;
  ciclo: string;
  horas_semanales: number;
  materia: { id: number; nombre: string };
  maestro: { id: number; nombre: string };
  seccion_grado: { id: number; nombre: string };
  alumnos: AlumnoResponse[];
}

// --- Notas (Bulk Upsert) ---
export interface NotaBulkRequest {
  alumno: number; // id del alumno
  tipo_nota: number; // id del tipo de nota
  materia_asignada: number; // id de la materia_asignada
  calificacion: number;
  fecha?: string; // opcional, el backend la pone si no se envía
}

export interface NotaBulkResponse {
  id: number;
  alumno: number;
  tipo_nota: number;
  materia_asignada: number;
  calificacion: number;
  fecha: string;
}

// --- ML Prediction Interfaces ---

/**
 * Respuesta de predicción de aprobado de materia usando ML
 * - probability: probabilidad de aprobación (0-1)
 * - aprobado: predicción binaria (true/false)
 * - features: objeto con los features usados en la predicción (notas por tipo, participaciones, asistencia, etc)
 */
export interface PrediccionAprobadoMateriaResponse {
  probability: number; // Probabilidad de aprobación (0-1)
  aprobado: boolean;   // Predicción binaria
  features: {
    [feature: string]: number; // Ej: nota_tipo_1, nota_tipo_2, cantidad_participaciones, promedio_participaciones, porcentaje_asistencia, promedio_nota, etc
  };
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  public router = inject(Router);

  // --- Endpoints centralizados ---
  private API_BASE = 'http://localhost:8000';
  private apiUrl = `${this.API_BASE}/auth/token/`;
  private perfilUrl = `${this.API_BASE}/api/personas/perfil/`;
  private inscripcionUrl = `${this.API_BASE}/api/personas/inscripcion/`;
  private materiaUrl = `${this.API_BASE}/api/materias/materias/`;
  private gradosUrl = `${this.API_BASE}/api/secciones/grados/`;
  private seccionesUrl = `${this.API_BASE}/api/secciones/secciones/`;
  private maestroUrl = `${this.API_BASE}/api/personas/maestros/`;
  private AlumnoUrl = `${this.API_BASE}/api/personas/alumnos/`;
  private tutorUrl = `${this.API_BASE}/api/personas/tutores/`;
  private seccionGradoUrl = `${this.API_BASE}/api/secciones/secciones-grado/`;
  private materiaAsignadaUrl = `${this.API_BASE}/api/materias/materias-asignadas/`;

  // --- Auth & Perfil ---
  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(this.apiUrl, { username, password }).pipe(
      tap((resp: any) => {
        localStorage.setItem('access_token', resp.access);
        this.getPerfil().subscribe();
      }),
      catchError(this.handleError)
    );
  }

  getPerfil(): Observable<PerfilResponse> {  // <--- Cambiado aquí
    return this.http.get<PerfilResponse>(this.perfilUrl).pipe(
      tap((profile: PerfilResponse) => {
        localStorage.setItem('perfil', JSON.stringify(profile));
      }),
      catchError(this.handleError)
    );
  }

  get perfil() {
    const perfilString = localStorage.getItem('perfil');
    return perfilString ? JSON.parse(perfilString) : null;
  }

  hasRole(role: string): boolean {
    return this.perfil?.roles?.includes(role) || false;
  }

  hasPrivilegio(priv: string): boolean {
    return this.perfil?.privilegios?.includes(priv) || false;
  }

  logout() {
    localStorage.removeItem('access_token');
    this.router.navigate(['/']);
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }

  private handleError(error: HttpErrorResponse) {
    return throwError(() => error);
  }

  // --- Materias CRUD ---
  getMaterias(): Observable<Materia[]> {
    return this.http.get<Materia[]>(this.materiaUrl).pipe(
      catchError(this.handleError)
    );
  }

  addMateria(materia: Partial<Materia>): Observable<Materia> {
    return this.http.post<Materia>(this.materiaUrl, materia).pipe(
      catchError(this.handleError)
    );
  }

  updateMateria(id: number, materia: Partial<Materia>): Observable<Materia> {
    return this.http.put<Materia>(`${this.materiaUrl}${id}/`, materia).pipe(
      catchError(this.handleError)
    );
  }

  deleteMateria(id: number): Observable<any> {
    return this.http.delete<any>(`${this.materiaUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  // --- Grados CRUD ---
  getGrados(activo?: boolean): Observable<Grado[]> {
    let params = {};
    if (typeof activo === 'boolean') {
      params = { activo };
    }
    return this.http.get<any>(this.gradosUrl, { params }).pipe(
      map((resp: any) => Array.isArray(resp) ? resp : (resp.results ?? [])),
      catchError(this.handleError)
    );
  }

  addGrado(grado: Partial<Grado>): Observable<Grado> {
    return this.http.post<Grado>(this.gradosUrl, grado).pipe(
      catchError(this.handleError)
    );
  }

  updateGrado(id: number, grado: Partial<Grado>): Observable<Grado> {
    return this.http.put<Grado>(`${this.gradosUrl}${id}/`, grado).pipe(
      catchError(this.handleError)
    );
  }

  deleteGrado(id: number): Observable<any> {
    return this.http.delete<any>(`${this.gradosUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  // --- Secciones CRUD ---
  getSecciones(activo?: boolean): Observable<Seccion[]> {
    let params = {};
    if (typeof activo === 'boolean') {
      params = { activo };
    }
    return this.http.get<Seccion[]>(this.seccionesUrl, { params }).pipe(
      catchError(this.handleError)
    );
  }

  addSeccion(seccion: Partial<Seccion>): Observable<Seccion> {
    // Solo envía el nombre
    const payload = { nombre: seccion.nombre };
    return this.http.post<Seccion>(this.seccionesUrl, payload).pipe(
      catchError(this.handleError)
    );
  }

  updateSeccion(id: number, seccion: Partial<Seccion>): Observable<Seccion> {
    // Solo envía el nombre
    const payload = { nombre: seccion.nombre };
    return this.http.put<Seccion>(`${this.seccionesUrl}${id}/`, payload).pipe(
      catchError(this.handleError)
    );
  }

  deleteSeccion(id: number): Observable<any> {
    return this.http.delete<any>(`${this.seccionesUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  // --- Inscripciones ---
  inscribirAlumno(data: InscripcionRequest): Observable<InscripcionResponse> {
    return this.http.post<InscripcionResponse>(this.inscripcionUrl, data).pipe(
      catchError(this.handleError)
    );
  }

  // --- Maestros CRUD ---
  getMaestros(): Observable<MaestroResponse[]> {
    return this.http.get<MaestroResponse[]>(this.maestroUrl).pipe(
      catchError(this.handleError)
    );
  }

  addMaestro(maestro: MaestroCreate): Observable<MaestroCreateResponse> {
    return this.http.post<MaestroCreateResponse>(this.maestroUrl, maestro).pipe(
      catchError(this.handleError)
    );
  }

  updateMaestro(id: number, maestro: MaestroCreate): Observable<MaestroResponse> {
    return this.http.put<MaestroResponse>(`${this.maestroUrl}${id}/`, maestro).pipe(
      catchError(this.handleError)
    );
  }

  deleteMaestro(id: number): Observable<any> {
    return this.http.delete<any>(`${this.maestroUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  // --- Maestros CRUD con paginación, búsqueda y reactivación ---
  getMaestrosPaginated(params: any): Observable<any> {
    return this.http.get<any>(this.maestroUrl, { params }).pipe(
      catchError(this.handleError)
    );
  }

  reactivarMaestro(id: number): Observable<any> {
    return this.http.post<any>(`${this.maestroUrl}${id}/reactivar/`, {}).pipe(
      catchError(this.handleError)
    );
  }

    // --- Alumnos CRUD ---
  getAlumnos(activo?: boolean): Observable<AlumnoResponse[]> {
    let params = {};
    if (typeof activo === 'boolean') {
      params = { activo };
    }
    return this.http.get<any>(this.AlumnoUrl, { params }).pipe(
      map((resp: any) => Array.isArray(resp) ? resp : (resp.results ?? [])),
      catchError(this.handleError)
    );
  }

  updateAlumno(id: number, alumno: AlumnoCreate): Observable<AlumnoResponse> {
    return this.http.put<AlumnoResponse>(`${this.AlumnoUrl}${id}/`, alumno).pipe(
      catchError(this.handleError)
    );
  }

  deleteAlumno(id: number): Observable<any> {
    return this.http.delete<any>(`${this.AlumnoUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  // --- Alumnos CRUD con paginación, búsqueda y reactivación ---
  getAlumnosPaginated(params: any): Observable<any> {
    return this.http.get<any>(this.AlumnoUrl, { params }).pipe(
      catchError(this.handleError)
    );
  }

  reactivarAlumno(id: number): Observable<any> {
    return this.http.post<any>(`${this.AlumnoUrl}${id}/reactivar/`, {}).pipe(
      catchError(this.handleError)
    );
  }
  // --- Tutores CRUD con paginación, búsqueda y reactivación ---
  getTutoresPaginated(params: any): Observable<any> {
    return this.http.get<any>(this.tutorUrl, { params }).pipe(
      catchError(this.handleError)
    );
  }

  reactivarTutor(id: number): Observable<any> {
    return this.http.post<any>(`${this.tutorUrl}${id}/reactivar/`, {}).pipe(
      catchError(this.handleError)
    );
  }

  asociarTutorAlumno(tutorId: number, alumnoId: number): Observable<any> {
    // Endpoint personalizado para asociar tutor y alumno existente
    return this.http.post<any>(`${this.tutorUrl}${tutorId}/asociar_alumno/`, { alumno_id: alumnoId }).pipe(
      catchError(this.handleError)
    );
  }

  actualizarAlumnosTutor(tutorId: number, alumnos_ids: number[]): Observable<any> {
    // Endpoint para actualizar la lista de alumnos asociados a un tutor
    return this.http.post<any>(`${this.tutorUrl}${tutorId}/actualizar_alumnos/`, { alumnos_ids }).pipe(
      catchError(this.handleError)
    );
  }

  // --- Tutores CRUD ---
  addTutor(tutor: TutorCreate): Observable<TutorCreateResponse> {
    return this.http.post<TutorCreateResponse>(this.tutorUrl, tutor).pipe(
      catchError(this.handleError)
    );
  }

  updateTutor(id: number, tutor: TutorCreate): Observable<TutorResponse> {
    return this.http.put<TutorResponse>(`${this.tutorUrl}${id}/`, tutor).pipe(
      catchError(this.handleError)
    );
  }

  deleteTutor(id: number): Observable<any> {
    return this.http.delete<any>(`${this.tutorUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  // --- Secciones CRUD con paginación, búsqueda y desactivación lógica ---
  getSeccionesPaginated(params: any): Observable<any> {
    return this.http.get<any>(this.seccionesUrl, { params }).pipe(
      catchError(this.handleError)
    );
  }

  desactivarSeccion(id: number): Observable<any> {
    return this.http.delete<any>(`${this.seccionesUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  reactivarSeccion(id: number): Observable<any> {
    return this.http.post<any>(`${this.seccionesUrl}${id}/reactivar/`, {}).pipe(
      catchError(this.handleError)
    );
  }

  // --- Grados CRUD con paginación, búsqueda y desactivación lógica ---
  getGradosPaginated(params: any): Observable<any> {
    return this.http.get<any>(this.gradosUrl, { params }).pipe(
      catchError(this.handleError)
    );
  }

  desactivarGrado(id: number): Observable<any> {
    return this.http.delete<any>(`${this.gradosUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  reactivarGrado(id: number): Observable<any> {
    return this.http.post<any>(`${this.gradosUrl}${id}/reactivar/`, {}).pipe(
      catchError(this.handleError)
    );
  }

  // --- Materias CRUD con paginación, búsqueda y desactivación lógica ---
  getMateriasPaginated(params: any): Observable<any> {
    return this.http.get<any>(this.materiaUrl, { params }).pipe(
      catchError(this.handleError)
    );
  }

  desactivarMateria(id: number): Observable<any> {
    return this.http.delete<any>(`${this.materiaUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  reactivarMateria(id: number): Observable<any> {
    return this.http.post<any>(`${this.materiaUrl}${id}/reactivar/`, {}).pipe(
      catchError(this.handleError)
    );
  }

  // --- SeccionGrado (Asignaciones) CRUD ---
  getSeccionGrados(params?: any): Observable<any> {
    return this.http.get<any>(this.seccionGradoUrl, { params }).pipe(
      catchError(this.handleError)
    );
  }

  addSeccionGrado(data: Partial<SeccionGrado>): Observable<SeccionGrado> {
    return this.http.post<SeccionGrado>(this.seccionGradoUrl, data).pipe(
      catchError(this.handleError)
    );
  }

  updateSeccionGrado(id: number, data: Partial<SeccionGrado>): Observable<SeccionGrado> {
    return this.http.put<SeccionGrado>(`${this.seccionGradoUrl}${id}/`, data).pipe(
      catchError(this.handleError)
    );
  }

  desactivarSeccionGrado(id: number): Observable<any> {
    return this.http.delete<any>(`${this.seccionGradoUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  reactivarSeccionGrado(id: number): Observable<any> {
    return this.http.post<any>(`${this.seccionGradoUrl}${id}/reactivar/`, {}).pipe(
      catchError(this.handleError)
    );
  }

  // --- MateriaAsignada (Asignación de Materias) CRUD con paginación y búsqueda ---
  getMateriasAsignadas(params?: any): Observable<any> {
    return this.http.get<any>(this.materiaAsignadaUrl, { params }).pipe(
      catchError(this.handleError)
    );
  }

  addMateriaAsignada(data: any): Observable<MateriaAsignada> {
    // data puede ser un objeto o un array (para batch)
    if (Array.isArray(data)) {
      // Si es batch, enviar múltiples peticiones y combinarlas
      return new Observable<MateriaAsignada>((observer: any) => {
        let completed = 0;
        let results: MateriaAsignada[] = [];
        data.forEach((item: any, idx: number) => {
          const payload = {
            ciclo: item.ciclo,
            horas_semanales: item.horas_semanales,
            materia_id: typeof item.materia === 'object' ? item.materia.id : item.materia,
            maestro_id: typeof item.maestro === 'object' ? item.maestro.id : item.maestro,
            seccion_grado_id: typeof item.seccion_grado === 'object' ? item.seccion_grado.id : (item.seccion_grado_id ?? item.seccion_grado_ids?.[0])
          };
          this.http.post<MateriaAsignada>(this.materiaAsignadaUrl, payload).pipe(
            catchError(this.handleError)
          ).subscribe({
            next: (res: any) => {
              results.push(res);
              completed++;
              if (completed === data.length) {
                observer.next(results as any);
                observer.complete();
              }
            },
            error: (err: any) => {
              observer.error(err);
            }
          });
        });
      });
    } else {
      // Individual
      const payload = {
        ciclo: data.ciclo,
        horas_semanales: data.horas_semanales,
        materia_id: typeof data.materia === 'object' ? data.materia.id : data.materia,
        maestro_id: typeof data.maestro === 'object' ? data.maestro.id : data.maestro,
        seccion_grado_id: typeof data.seccion_grado === 'object' ? data.seccion_grado.id : (data.seccion_grado_id ?? data.seccion_grado_ids?.[0])
      };
      return this.http.post<MateriaAsignada>(this.materiaAsignadaUrl, payload).pipe(
        catchError(this.handleError)
      );
    }
  }

  updateMateriaAsignada(id: number, data: any): Observable<MateriaAsignada> {
    const payload = {
      ciclo: data.ciclo,
      horas_semanales: data.horas_semanales,
      materia_id: data.materia,
      maestro_id: data.maestro,
      seccion_grado_id: data.seccion_grado || data.seccion_grado_id || data.seccion_grado_ids?.[0]
    };
    return this.http.put<MateriaAsignada>(`${this.materiaAsignadaUrl}${id}/`, payload).pipe(
      catchError(this.handleError)
    );
  }

  deleteMateriaAsignada(id: number): Observable<any> {
    return this.http.delete<any>(`${this.materiaAsignadaUrl}${id}/`).pipe(
      catchError(this.handleError)
    );
  }

  // --- Materias asignadas por maestro, con alumnos por materia/seccion_grado/ciclo ---
  getMateriasAsignadasPorMaestro(maestroId: number, ciclo?: string): Observable<MateriaAsignadaConAlumnos[]> {
    const params: any = { maestro: maestroId };
    if (ciclo) params.ciclo = ciclo;
    return this.http.get<MateriaAsignadaConAlumnos[]>(`${this.materiaAsignadaUrl}por-maestro/`, { params }).pipe(
      catchError(this.handleError)
    );
  }

  // --- Tipos de nota ---
  crearTipoNota(data: { nombre: string; peso: number; orden: number; materia_asignada: number }) {
    return this.http.post<any>(`${this.API_BASE}/api/materias/tipos-nota/`, data);
  }

  /**
   * Obtiene los tipos de nota para una materia_asignada específica
   * @param materiaAsignadaId id de la materia_asignada
   */
  getTiposNotaPorMateriaAsignada(materiaAsignadaId: number) {
    return this.http.get<any[]>(`${this.API_BASE}/api/materias/tipos-nota/por-materia-asignada/`, {
      params: { materia_asignada: materiaAsignadaId }
    }).pipe(
      catchError(this.handleError)
    );
  }

  bulkUpsertNotas(notas: NotaBulkRequest[]) {
    return this.http.post<NotaBulkResponse[]>(
      `${this.API_BASE}/api/evaluacion/notas/bulk/`,
      notas
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene todas las notas de los alumnos para una materia_asignada específica
   * @param materiaAsignadaId id de la materia_asignada
   */
  getNotasPorMateriaAsignada(materiaAsignadaId: number) {
    return this.http.get<any[]>(`${this.API_BASE}/api/evaluacion/notas/`, {
      params: { materia_asignada: materiaAsignadaId }
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Registra o actualiza asistencias en masa (upsert por alumno, materia_asignada y fecha)
   * @param asistencias Array de asistencias: { alumno, materia_asignada, fecha, estado }
   */
  bulkUpsertAsistencias(asistencias: any[]) {
    return this.http.post<any[]>(
      `${this.API_BASE}/api/evaluacion/asistencias/bulk/`,
      asistencias
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene las asistencias de los alumnos para una materia_asignada y fecha específica
   * @param materiaAsignadaId id de la materia_asignada
   * @param fecha fecha en formato YYYY-MM-DD
   */
  getAsistenciasPorMateriaYFecha(materiaAsignadaId: number, fecha: string) {
    return this.http.get<any[]>(`${this.API_BASE}/api/evaluacion/asistencias/por-materia-y-fecha/`, {
      params: { materia_asignada: materiaAsignadaId, fecha }
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Registra o actualiza participaciones en masa (upsert por alumno, materia_asignada y fecha)
   * @param participaciones Array de participaciones: { alumno, materia_asignada, fecha, puntaje, observacion }
   */
  bulkUpsertParticipaciones(participaciones: any[]) {
    return this.http.post<any[]>(
      `${this.API_BASE}/api/evaluacion/participaciones/bulk/`,
      participaciones
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene las participaciones de los alumnos para una materia_asignada y fecha específica
   * @param materiaAsignadaId id de la materia_asignada
   * @param fecha fecha en formato YYYY-MM-DD
   */
  getParticipacionesPorMateriaYFecha(materiaAsignadaId: number, fecha: string) {
    return this.http.get<any[]>(`${this.API_BASE}/api/evaluacion/participaciones/por-materia-y-fecha/`, {
      params: { materia_asignada: materiaAsignadaId, fecha }
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Predice si un alumno aprobará una materia usando ML (envía features desde el frontend)
   * @param features Objeto con todos los features requeridos por el modelo ML
   * @returns Observable<PrediccionAprobadoMateriaResponse> con probabilidad, aprobado y features usados
   */
  predecirAprobadoAuto(features: { [feature: string]: number }): Observable<PrediccionAprobadoMateriaResponse> {
    return this.http.post<PrediccionAprobadoMateriaResponse>(`${this.API_BASE}/api/evaluacion/predecir-aprobado-auto/`, features).pipe(
      map(resp => {
        // Si la respuesta tiene 'probabilidad', renómbrala a 'probability' para mantener consistencia
        if ('probabilidad' in resp && !('probability' in resp)) {
          (resp as any).probability = (resp as any).probabilidad;
          delete (resp as any).probabilidad;
        }
        return resp;
      }),
      catchError(this.handleError)
    );
  }

  /**
   * Predice si un alumno aprobará un examen usando ML (el backend arma los features)
   * @param params objeto con ciclo, materia_asignada, alumno, tipo_examen
   */
  predecirAprobadoExamen(params: { ciclo: string, materia_asignada: number, alumno: number, tipo_examen: string }): Observable<any> {
    return this.http.post<any>(`${this.API_BASE}/api/ml/predict-exam/`, params).pipe(
      catchError(this.handleError)
    );
  }
}
