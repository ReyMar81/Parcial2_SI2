import { Component, OnInit } from '@angular/core';
import { AuthService, AlumnoResponse } from '../../auth.service';
import { AlumnoFormDialogComponent } from './alumnos-form-dialog.component';
import { DeleteAlumnoConfirmDialogComponent } from './delete-confirm-dialog.component';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { CommonModule } from '@angular/common';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { PageEvent } from '@angular/material/paginator';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule } from '@angular/material/paginator';

@Component({
  selector: 'app-alumnos',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatIconModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatFormFieldModule,
    MatInputModule,
    MatPaginatorModule,
    AlumnoFormDialogComponent,
    DeleteAlumnoConfirmDialogComponent,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  templateUrl: './alumnos.component.html',
  styleUrls: ['./alumnos.component.css']
})
export class AlumnosComponent implements OnInit {
  alumnos: AlumnoResponse[] = [];
  alert: { type: string, message: string } | null = null;
  activos = true;
  search = '';
  page = 1;
  pageSize = 10;
  total = 0;

  constructor(
    private authService: AuthService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadAlumnos();
  }

  loadAlumnos() {
    const params: any = {
      activo: this.activos,
      page: this.page,
      page_size: this.pageSize
    };
    if (this.search) params.search = this.search;
    this.authService.getAlumnosPaginated(params).subscribe({
      next: (resp: any) => {
        this.alumnos = resp.results;
        this.total = resp.count;
      },
      error: () => this.showAlert('error', 'Error al cargar alumnos.')
    });
  }

  onToggleActivos(activos: boolean) {
    this.activos = activos;
    this.page = 1;
    this.loadAlumnos();
  }

  onSearchChange(value: string) {
    this.search = value;
    this.page = 1;
    this.loadAlumnos();
  }

  onPageChange(event: PageEvent) {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadAlumnos();
  }

  openEditAlumno(alumno: AlumnoResponse) {
    const dialogRef = this.dialog.open(AlumnoFormDialogComponent, {
      width: '500px',
      data: { alumno, isEdit: true }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.showAlert('success', 'Alumno editado exitosamente.');
        this.loadAlumnos();
      }
    });
  }

  openDeactivateDialog(alumno: AlumnoResponse) {
    const dialogRef = this.dialog.open(DeleteAlumnoConfirmDialogComponent, {
      width: '350px',
      data: { nombre: alumno.persona.nombre + ' ' + alumno.persona.apellido_paterno, desactivar: true }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.authService.deleteAlumno(alumno.id!).subscribe({
          next: () => {
            this.showAlert('success', 'Alumno desactivado correctamente.');
            this.loadAlumnos();
          },
          error: () => this.showAlert('error', 'No se pudo desactivar el alumno.')
        });
      }
    });
  }

  reactivarAlumno(alumno: AlumnoResponse) {
    this.authService.reactivarAlumno(alumno.id!).subscribe({
      next: () => {
        this.showAlert('success', 'Alumno reactivado correctamente.');
        this.loadAlumnos();
      },
      error: () => this.showAlert('error', 'No se pudo reactivar el alumno.')
    });
  }

  showAlert(type: string, message: string) {
    this.alert = { type, message };
    setTimeout(() => { this.alert = null; }, 3000);
  }
}
