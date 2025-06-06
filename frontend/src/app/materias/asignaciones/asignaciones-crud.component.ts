import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { AsignacionFormDialogComponent } from './asignacion-form-dialog.component';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { DeleteAsignacionConfirmDialogComponent } from './delete-asignacion-confirm-dialog.component';

export interface Asignacion {
  id: number;
  ciclo: string;
  materia: string;
  maestro: string;
  seccion: string;
  horas_semanales: number;
}

@Component({
  selector: 'app-asignaciones-crud',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    AsignacionFormDialogComponent,
    MatIconModule,
    MatButtonModule,
    DeleteAsignacionConfirmDialogComponent
  ],
  templateUrl: './asignaciones-crud.component.html',
  styleUrls: ['./asignaciones-crud.component.css'],
})
export class AsignacionesCrudComponent {
  asignaciones: Asignacion[] = [
    {
      id: 1,
      ciclo: '2024-2025',
      materia: 'Matemáticas',
      maestro: 'Juan Pérez',
      seccion: '5A',
      horas_semanales: 5
    },
    {
      id: 2,
      ciclo: '2024-2025',
      materia: 'Ciencias',
      maestro: 'Ana Gómez',
      seccion: '5B',
      horas_semanales: 4
    }
  ];
  nextId = 3;
  alert: { type: 'success' | 'error' | 'warning', message: string } | null = null;
  deleteDialogRef: any = null;
  deleteTarget: Asignacion | null = null;

  constructor(private dialog: MatDialog) {}

  openAddAsignacion() {
    const dialogRef = this.dialog.open(AsignacionFormDialogComponent, {
      width: '400px',
      data: {}
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        this.asignaciones.push({ id: this.nextId++, ...result });
        this.showAlert('success', 'Asignación agregada correctamente');
      }
    });
  }

  openEditAsignacion(asignacion: Asignacion) {
    const dialogRef = this.dialog.open(AsignacionFormDialogComponent, {
      width: '400px',
      data: { asignacion }
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        Object.assign(asignacion, result);
        this.showAlert('success', 'Asignación editada correctamente');
      }
    });
  }

  openDeleteDialog(asignacion: Asignacion) {
    this.deleteTarget = asignacion;
    this.deleteDialogRef = this.dialog.open(DeleteAsignacionConfirmDialogComponent, {
      width: '350px',
      data: {
        materia: asignacion.materia,
        seccion: asignacion.seccion,
        ciclo: asignacion.ciclo
      }
    });
    this.deleteDialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.deleteAsignacion(asignacion);
      }
      this.deleteTarget = null;
    });
  }

  deleteAsignacion(asignacion: Asignacion) {
    this.asignaciones = this.asignaciones.filter(a => a.id !== asignacion.id);
    this.showAlert('warning', 'Asignación eliminada');
  }

  showAlert(type: 'success' | 'error' | 'warning', message: string) {
    this.alert = { type, message };
    setTimeout(() => this.alert = null, 3000);
  }
}
