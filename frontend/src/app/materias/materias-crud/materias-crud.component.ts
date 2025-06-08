import { Component, OnInit } from '@angular/core';
import { AuthService, Materia } from '../../auth.service';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MateriaFormDialogComponent } from './materia-form-dialog.component';
import { DeleteMateriaConfirmDialogComponent } from './delete-confirm-dialog.component';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatButtonToggleModule } from '@angular/material/button-toggle';

@Component({
  selector: 'app-materias-crud',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatIconModule,
    MatButtonModule,
    MatPaginatorModule,
    MatButtonToggleModule,
    MateriaFormDialogComponent,
    DeleteMateriaConfirmDialogComponent
  ],
  templateUrl: './materias-crud.component.html',
  styleUrls: ['./materias-crud.component.css']
})
export class MateriasCrudComponent implements OnInit {
  materias: Materia[] = [];
  alert: { type: string, message: string } | null = null;
  search = '';
  page = 1;
  pageSize = 10;
  total = 0;
  activos = true;

  constructor(
    private authService: AuthService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadMaterias();
  }

  loadMaterias() {
    const params: any = {
      activo: this.activos,
      page: this.page,
      page_size: this.pageSize
    };
    if (this.search) params.search = this.search;
    this.authService.getMateriasPaginated(params).subscribe({
      next: (resp: any) => {
        this.materias = resp.results;
        this.total = resp.count;
      },
      error: () => this.showAlert('error', 'Error al cargar materias.')
    });
  }

  onSearchChange(value: string) {
    this.search = value;
    this.page = 1;
    this.loadMaterias();
  }

  onPageChange(event: any) {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadMaterias();
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

  onToggleActivos(event: any) {
    this.activos = event.value;
    this.page = 1;
    this.loadMaterias();
  }

  desactivarMateria(materia: Materia) {
    this.authService.desactivarMateria(materia.id!).subscribe({
      next: () => {
        this.showAlert('warning', 'Materia desactivada.');
        this.loadMaterias();
      },
      error: () => this.showAlert('error', 'No se pudo desactivar la materia.')
    });
  }

  reactivarMateria(materia: Materia) {
    this.authService.reactivarMateria(materia.id!).subscribe({
      next: () => {
        this.showAlert('success', 'Materia reactivada.');
        this.loadMaterias();
      },
      error: () => this.showAlert('error', 'No se pudo reactivar la materia.')
    });
  }

  showAlert(type: string, message: string) {
    this.alert = { type, message };
    setTimeout(() => { this.alert = null; }, 3000);
  }
}
