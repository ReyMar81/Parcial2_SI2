import { Component, OnInit } from '@angular/core';
import { AuthService, PersonaResponse, AlumnoResponse } from '../../auth.service';
import { TutorFormDialogComponent } from './tutor-form-dialog.component';
import { DeleteTutorConfirmDialogComponent } from './delete-tutor-confirm-dialog.component';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { CommonModule } from '@angular/common';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { TutorCredencialesDialogComponent } from './tutor-credenciales-dialog.component';
import { AlumnoFormDialogComponent } from '../alumnos/alumnos-form-dialog.component';
import { MatListModule } from '@angular/material/list';
import { PageEvent } from '@angular/material/paginator';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule } from '@angular/material/paginator';

export interface TutorResponse {
  id: number;
  persona: PersonaResponse;
  ocupacion: string;
  alumnos_asociados?: AlumnoResponse[];
  registro?: string;
}

@Component({
  selector: 'app-tutores',
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
    TutorFormDialogComponent,
    TutorCredencialesDialogComponent,
    AlumnoFormDialogComponent,
    DeleteTutorConfirmDialogComponent,
    MatDatepickerModule,
    MatNativeDateModule,
    MatListModule
  ],
  templateUrl: './tutores.component.html',
  styleUrls: ['./tutores.component.css']
})
export class TutoresComponent implements OnInit {
  tutores: TutorResponse[] = [];
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
    this.loadTutores();
  }

  loadTutores() {
    const params: any = {
      activo: this.activos,
      page: this.page,
      page_size: this.pageSize
    };
    if (this.search) params.search = this.search;
    this.authService.getTutoresPaginated(params).subscribe({
      next: (resp: any) => {
        this.tutores = resp.results;
        this.total = resp.count;
      },
      error: () => this.showAlert('error', 'Error al cargar tutores.')
    });
  }

  onToggleActivos(activos: boolean) {
    this.activos = activos;
    this.page = 1;
    this.loadTutores();
  }

  onSearchChange(value: string) {
    this.search = value;
    this.page = 1;
    this.loadTutores();
  }

  onPageChange(event: PageEvent) {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadTutores();
  }

  openAddTutor() {
    const dialogRef = this.dialog.open(TutorFormDialogComponent, {
      width: '500px',
      data: { isEdit: false }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.showAlert('success', 'Tutor agregado exitosamente.');
        this.loadTutores();
      }
    });
  }

  openEditTutor(tutor: TutorResponse) {
    // Hacer copia profunda para evitar mutación por referencia
    const tutorCopy: TutorResponse = JSON.parse(JSON.stringify(tutor));
    const dialogRef = this.dialog.open(TutorFormDialogComponent, {
      width: '500px',
      data: { tutor: tutorCopy, isEdit: true }
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        this.showAlert('success', 'Tutor editado exitosamente.');
        this.loadTutores();
      }
    });
  }

  openDeactivateDialog(tutor: TutorResponse) {
    const dialogRef = this.dialog.open(DeleteTutorConfirmDialogComponent, {
      width: '350px',
      data: { nombre: tutor.persona.nombre + ' ' + tutor.persona.apellido_paterno, desactivar: true }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.authService.deleteTutor(tutor.id!).subscribe({
          next: () => {
            this.showAlert('success', 'Tutor desactivado correctamente.');
            this.loadTutores();
          },
          error: () => this.showAlert('error', 'No se pudo desactivar el tutor.')
        });
      }
    });
  }

  reactivarTutor(tutor: TutorResponse) {
    this.authService.reactivarTutor(tutor.id!).subscribe({
      next: () => {
        this.showAlert('success', 'Tutor reactivado correctamente.');
        this.loadTutores();
      },
      error: () => this.showAlert('error', 'No se pudo reactivar el tutor.')
    });
  }

  showAlert(type: string, message: string) {
    this.alert = { type, message };
    setTimeout(() => { this.alert = null; }, 3000);
  }
}
