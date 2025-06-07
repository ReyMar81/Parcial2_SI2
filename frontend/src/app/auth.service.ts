import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

// ---- Interfaces ----

// Materia
export interface Materia {
  id?: number;
  nombre: string;
  descripcion: string;
}

// Grado
export interface Grado {
  id?: number;
  nombre: string;
  nivel?: string;
  descripcion?: string;
}

// Seccion
export interface Seccion {
  id?: number;
  nombre: string;
  aula: string;
  capacidad_maxima: number;
  estado: 'activa' | 'cerrada';
  grado: number | Grado;
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
  tutor: {
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
  tipo_relacion: string;
  seccion_id: number;
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
  getGrados(): Observable<Grado[]> {
    return this.http.get<Grado[]>(this.gradosUrl).pipe(
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
  getSecciones(): Observable<Seccion[]> {
    return this.http.get<Seccion[]>(this.seccionesUrl).pipe(
      catchError(this.handleError)
    );
  }

  addSeccion(seccion: Partial<Seccion>): Observable<Seccion> {
    return this.http.post<Seccion>(this.seccionesUrl, seccion).pipe(
      catchError(this.handleError)
    );
  }

  updateSeccion(id: number, seccion: Partial<Seccion>): Observable<Seccion> {
    return this.http.put<Seccion>(`${this.seccionesUrl}${id}/`, seccion).pipe(
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
}
