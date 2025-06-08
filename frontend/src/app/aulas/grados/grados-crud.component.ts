import { Component, OnInit } from '@angular/core';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { GradoFormDialogComponent } from './grado-form-dialog.component';
import { DeleteGradoConfirmDialogComponent } from './delete-grado-confirm-dialog.component';
import { AuthService, Grado } from '../../auth.service';
import { FormsModule } from '@angular/forms';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatButtonToggleModule } from '@angular/material/button-toggle';

@Component({
  selector: 'app-grados-crud',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatIconModule,
    MatButtonModule,
    MatPaginatorModule,
    MatButtonToggleModule,
    GradoFormDialogComponent,
    DeleteGradoConfirmDialogComponent
  ],
  templateUrl: './grados-crud.component.html',
  styleUrls: ['./grados-crud.component.css']
})
export class GradosCrudComponent implements OnInit {
  grados: Grado[] = [];
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
    this.loadGrados();
  }

  loadGrados() {
    const params: any = {
      activo: this.activos,
      page: this.page,
      page_size: this.pageSize
    };
    if (this.search) params.search = this.search;
    this.authService.getGradosPaginated(params).subscribe({
      next: (resp: any) => {
        this.grados = resp.results;
        this.total = resp.count;
      },
      error: () => this.showAlert('error', 'Error al cargar grados.')
    });
  }

  onSearchChange(value: string) {
    this.search = value;
    this.page = 1;
    this.loadGrados();
  }

  onPageChange(event: any) {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadGrados();
  }

  openAddGrado() {
    const dialogRef = this.dialog.open(GradoFormDialogComponent, {
      width: '500px',
      data: {}
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.showAlert('success', 'Grado agregado exitosamente.');
        this.loadGrados();
      }
    });
  }

  openEditGrado(grado: Grado) {
    const dialogRef = this.dialog.open(GradoFormDialogComponent, {
      width: '500px',
      data: { grado }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.showAlert('success', 'Grado editado exitosamente.');
        this.loadGrados();
      }
    });
  }

  openDeleteDialog(grado: Grado) {
    const dialogRef = this.dialog.open(DeleteGradoConfirmDialogComponent, {
      width: '400px',
      data: { nombre: grado.nombre }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.authService.deleteGrado(grado.id!).subscribe({
          next: () => {
            this.showAlert('success', 'Grado eliminado.');
            this.loadGrados();
          },
          error: () => this.showAlert('error', 'No se pudo eliminar el grado.')
        });
      }
    });
  }

  onToggleActivos(event: any) {
    this.activos = event.value;
    this.page = 1;
    this.loadGrados();
  }

  desactivarGrado(grado: Grado) {
    this.authService.desactivarGrado(grado.id!).subscribe({
      next: () => {
        this.showAlert('warning', 'Grado desactivado.');
        this.loadGrados();
      },
      error: () => this.showAlert('error', 'No se pudo desactivar el grado.')
    });
  }

  reactivarGrado(grado: Grado) {
    this.authService.reactivarGrado(grado.id!).subscribe({
      next: () => {
        this.showAlert('success', 'Grado reactivado.');
        this.loadGrados();
      },
      error: () => this.showAlert('error', 'No se pudo reactivar el grado.')
    });
  }

  showAlert(type: string, message: string) {
    this.alert = { type, message };
    setTimeout(() => { this.alert = null; }, 3000);
  }
}
