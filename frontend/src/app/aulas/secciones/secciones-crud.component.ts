import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { SeccionFormDialogComponent, Seccion } from './seccion-form-dialog.component';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { DeleteSeccionConfirmDialogComponent } from './delete-seccion-confirm-dialog.component';

@Component({
  selector: 'app-secciones-crud',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    SeccionFormDialogComponent,
    MatIconModule,
    MatButtonModule,
    DeleteSeccionConfirmDialogComponent
  ],
  templateUrl: './secciones-crud.component.html',
  styleUrls: ['./secciones-crud.component.css'],
})
export class SeccionesCrudComponent {
  secciones: Seccion[] = [
    { id: 1, nombre: 'A', aula: '101', capacidad_maxima: 30, estado: true, grado: 'Primer Grado' },
    { id: 2, nombre: 'B', aula: '102', capacidad_maxima: 28, estado: true, grado: 'Segundo Grado' },
    { id: 3, nombre: 'C', aula: '201', capacidad_maxima: 32, estado: false, grado: 'Tercer Grado' }
  ];
  nextId = 4;
  alert: { type: 'success' | 'error' | 'warning', message: string } | null = null;
  deleteDialogRef: any = null;
  deleteTarget: Seccion | null = null;
  grados: string[] = ['Primer Grado', 'Segundo Grado', 'Tercer Grado'];

  constructor(private dialog: MatDialog) {}

  openAddSeccion() {
    const dialogRef = this.dialog.open(SeccionFormDialogComponent, {
      width: '400px',
      data: { grados: this.grados }
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        this.secciones.push({ id: this.nextId++, ...result });
        this.showAlert('success', 'Sección agregada correctamente');
      }
    });
  }

  openEditSeccion(seccion: Seccion) {
    const dialogRef = this.dialog.open(SeccionFormDialogComponent, {
      width: '400px',
      data: { seccion, grados: this.grados }
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        Object.assign(seccion, result);
        this.showAlert('success', 'Sección editada correctamente');
      }
    });
  }

  openDeleteDialog(seccion: Seccion) {
    this.deleteTarget = seccion;
    this.deleteDialogRef = this.dialog.open(DeleteSeccionConfirmDialogComponent, {
      width: '350px',
      data: { nombre: seccion.nombre }
    });
    this.deleteDialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.deleteSeccion(seccion);
      }
      this.deleteTarget = null;
    });
  }

  deleteSeccion(seccion: Seccion) {
    this.secciones = this.secciones.filter(s => s.id !== seccion.id);
    this.showAlert('warning', 'Sección eliminada');
  }

  showAlert(type: 'success' | 'error' | 'warning', message: string) {
    this.alert = { type, message };
    setTimeout(() => this.alert = null, 3000);
  }
}
