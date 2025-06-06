import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { GradoFormDialogComponent } from './grado-form-dialog.component';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { DeleteGradoConfirmDialogComponent } from './delete-grado-confirm-dialog.component';

export interface Grado {
  id: number;
  nombre: string;
  nivel?: string;
  descripcion?: string;
}

@Component({
  selector: 'app-grados-crud',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    GradoFormDialogComponent,
    MatIconModule,
    MatButtonModule,
    DeleteGradoConfirmDialogComponent
  ],
  templateUrl: './grados-crud.component.html',
  styleUrls: ['./grados-crud.component.css'],
})
export class GradosCrudComponent {
  grados: Grado[] = [
    { id: 1, nombre: 'Primer Grado', nivel: 'Básico', descripcion: 'Primer año escolar' },
    { id: 2, nombre: 'Segundo Grado', nivel: 'Básico', descripcion: 'Segundo año escolar' },
    { id: 3, nombre: 'Tercer Grado', nivel: 'Básico', descripcion: 'Tercer año escolar' }
  ];
  nextId = 4;
  alert: { type: 'success' | 'error' | 'warning', message: string } | null = null;
  deleteDialogRef: any = null;
  deleteTarget: Grado | null = null;

  constructor(private dialog: MatDialog) {}

  openAddGrado() {
    const dialogRef = this.dialog.open(GradoFormDialogComponent, {
      width: '400px',
      data: {}
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        this.grados.push({ id: this.nextId++, ...result });
        this.showAlert('success', 'Grado agregado correctamente');
      }
    });
  }

  openEditGrado(grado: Grado) {
    const dialogRef = this.dialog.open(GradoFormDialogComponent, {
      width: '400px',
      data: { grado }
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        Object.assign(grado, result);
        this.showAlert('success', 'Grado editado correctamente');
      }
    });
  }

  openDeleteDialog(grado: Grado) {
    this.deleteTarget = grado;
    this.deleteDialogRef = this.dialog.open(DeleteGradoConfirmDialogComponent, {
      width: '350px',
      data: { nombre: grado.nombre }
    });
    this.deleteDialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.deleteGrado(grado);
      }
      this.deleteTarget = null;
    });
  }

  deleteGrado(grado: Grado) {
    this.grados = this.grados.filter(g => g.id !== grado.id);
    this.showAlert('warning', 'Grado eliminado');
  }

  showAlert(type: 'success' | 'error' | 'warning', message: string) {
    this.alert = { type, message };
    setTimeout(() => this.alert = null, 3000);
  }
}
