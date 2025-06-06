import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { DeleteConfirmDialogComponent } from './delete-confirm-dialog.component';
import { MateriaFormDialogComponent } from './materia-form-dialog.component';

// El modelo Materia se importa solo si se requiere como tipo, no se conecta a ningún servicio ni backend.
export interface Materia {
  id: number;
  nombre: string;
  descripcion?: string;
}

@Component({
  selector: 'app-materias-crud',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MateriaFormDialogComponent,
    MatIconModule,
    MatButtonModule,
    DeleteConfirmDialogComponent
  ],
  templateUrl: './materias-crud.component.html',
  styleUrls: ['./materias-crud.component.css'],
})
export class MateriasCrudComponent {
  materias: Materia[] = [
    { id: 1, nombre: 'Matemáticas', descripcion: 'Números y operaciones' },
    { id: 2, nombre: 'Lengua', descripcion: 'Gramática y literatura' },
    { id: 3, nombre: 'Ciencias', descripcion: 'Física, química y biología' }
  ];
  nextId = 4;
  alert: { type: 'success' | 'error' | 'warning', message: string } | null = null;
  deleteDialogRef: any = null;
  deleteTarget: Materia | null = null;

  constructor(private dialog: MatDialog) {}

  openAddMateria() {
    const dialogRef = this.dialog.open(MateriaFormDialogComponent, {
      width: '400px',
      data: {}
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        this.materias.push({ id: this.nextId++, ...result });
        this.showAlert('success', 'Materia agregada correctamente');
      }
    });
  }

  openEditMateria(materia: Materia) {
    const dialogRef = this.dialog.open(MateriaFormDialogComponent, {
      width: '400px',
      data: { materia }
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        Object.assign(materia, result);
        this.showAlert('success', 'Materia editada correctamente');
      }
    });
  }

  openDeleteDialog(materia: Materia) {
    this.deleteTarget = materia;
    this.deleteDialogRef = this.dialog.open(DeleteConfirmDialogComponent, {
      width: '350px',
      data: { nombre: materia.nombre }
    });
    this.deleteDialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.deleteMateria(materia);
      }
      this.deleteTarget = null;
    });
  }

  deleteMateria(materia: Materia) {
    this.materias = this.materias.filter(m => m.id !== materia.id);
    this.showAlert('warning', 'Materia eliminada');
  }

  showAlert(type: 'success' | 'error' | 'warning', message: string) {
    this.alert = { type, message };
    setTimeout(() => this.alert = null, 3000);
  }
}
