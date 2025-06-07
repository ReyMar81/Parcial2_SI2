import { Component, OnInit } from '@angular/core';
import { AuthService, Materia } from '../../auth.service';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MateriaFormDialogComponent } from './materia-form-dialog.component';
import { DeleteMateriaConfirmDialogComponent } from './delete-confirm-dialog.component';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-materias-crud',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatIconModule,
    MatButtonModule,
    MateriaFormDialogComponent,
    DeleteMateriaConfirmDialogComponent
  ],
  templateUrl: './materias-crud.component.html',
  styleUrls: ['./materias-crud.component.css']
})
export class MateriasCrudComponent implements OnInit {
  materias: Materia[] = [];
  alert: { type: string, message: string } | null = null;

  constructor(
    private authService: AuthService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadMaterias();
  }

  loadMaterias() {
    this.authService.getMaterias().subscribe({
      next: (data) => this.materias = data,
      error: () => this.showAlert('error', 'Error al cargar materias.')
    });
  }

  openAddMateria() {
    const dialogRef = this.dialog.open(MateriaFormDialogComponent, {
      width: '400px',
      data: { isEdit: false }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.showAlert('success', 'Materia agregada exitosamente.');
        this.loadMaterias();
      }
    });
  }

  openEditMateria(materia: Materia) {
    const dialogRef = this.dialog.open(MateriaFormDialogComponent, {
      width: '400px',
      data: { materia, isEdit: true }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.showAlert('success', 'Materia editada exitosamente.');
        this.loadMaterias();
      }
    });
  }

  openDeleteDialog(materia: Materia) {
    const dialogRef = this.dialog.open(DeleteMateriaConfirmDialogComponent, {
      width: '350px',
      data: { nombre: materia.nombre }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.authService.deleteMateria(materia.id!).subscribe({
          next: () => {
            this.showAlert('success', 'Materia eliminada.');
            this.loadMaterias();
          },
          error: () => this.showAlert('error', 'No se pudo eliminar la materia.')
        });
      }
    });
  }

  showAlert(type: string, message: string) {
    this.alert = { type, message };
    setTimeout(() => { this.alert = null; }, 3000);
  }
}
