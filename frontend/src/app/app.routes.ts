import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { PerfilComponent } from './perfil/perfil.component';
import { CambiarPasswordComponent } from './cambiar-password/cambiar-password.component';
import { DashboardWelcomeComponent } from './dashboard-welcome/dashboard-welcome.component';
import { GradosCrudComponent } from './aulas/grados/grados-crud.component';
import { SeccionesCrudComponent } from './aulas/secciones/secciones-crud.component';

export const routes: Routes = [
  { path: '', component: LoginComponent },
  {
    path: 'home',
    component: HomeComponent,
    children: [
      { path: '', component: DashboardWelcomeComponent },
      {
        path: 'usuarios',
        children: [
          { path: 'alumnos', loadComponent: () => import('./usuarios/alumnos/alumnos.component').then(m => m.AlumnosComponent) },
          { path: 'maestros', loadComponent: () => import('./usuarios/maestros/maestros.component').then(m => m.MaestrosComponent) },
          { path: 'tutores', loadComponent: () => import('./usuarios/tutores/tutores.component').then(m => m.TutoresComponent) },
          { path: 'admin', loadComponent: () => import('./usuarios/admin-usuario/admin-usuario.component').then(m => m.AdminUsuarioComponent) },
        ]
      },
      {
        path: 'materias',
        children: [
          { path: '', loadComponent: () => import('./materias/materias-crud/materias-crud.component').then(m => m.MateriasCrudComponent) },
          { path: 'asignaciones', loadComponent: () => import('./materias/asignaciones/asignaciones-crud.component').then(m => m.AsignacionesCrudComponent) },
        ]
      },
      {
        path: 'aulas',
        children: [
          { path: 'grados', component: GradosCrudComponent },
          { path: 'secciones', component: SeccionesCrudComponent },
          { path: 'asignaciones', loadComponent: () => import('./aulas/asignaciones/asignaciones.component').then(m => m.AsignacionesComponent) },
        ]
      },
      { path: 'inscripcion', loadComponent: () => import('./inscripcion/inscripcion.component').then(m => m.InscripcionFormComponent) },
      { path: 'perfil', component: PerfilComponent },
      { path: 'cambiar-password', component: CambiarPasswordComponent },
    ]
  }
];
