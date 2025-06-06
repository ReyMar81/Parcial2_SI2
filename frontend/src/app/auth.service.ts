import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  // Cambiar router a público para acceso desde componentes
  public router = inject(Router);
  private apiUrl = 'http://localhost:8000/auth/token/';
  private perfilUrl = 'http://localhost:8000/api/personas/perfil/';

  getPerfil(): Observable<any> {
    return this.http.get<any>(this.perfilUrl).pipe(
        tap((profile: any) => {
        // Aquí puedes guardar roles, privilegios, usuario, etc.
        localStorage.setItem('perfil', JSON.stringify(profile));
        }),
        catchError(this.handleError)
    );
    }

  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(this.apiUrl, { username, password }).pipe(
      tap((resp: any) => {
        localStorage.setItem('access_token', resp.access);
        this.getPerfil().subscribe();
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
}
