import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { SeccionFormDialogComponent } from './seccion-form-dialog.component';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { DeleteSeccionConfirmDialogComponent } from './delete-seccion-confirm-dialog.component';
import { AuthService, Seccion } from '../../auth.service';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { FormsModule } from '@angular/forms';
import { MatPaginatorModule } from '@angular/material/paginator';

@Component({
  selector: 'app-secciones-crud',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    SeccionFormDialogComponent,
    MatIconModule,
    MatButtonModule,
    DeleteSeccionConfirmDialogComponent,
    MatButtonToggleModule,
    MatPaginatorModule
  ],
  templateUrl: './secciones-crud.component.html',
  styleUrls: ['./secciones-crud.component.css'],
})
export class SeccionesCrudComponent implements OnInit {
  secciones: Seccion[] = [];
  alert: { type: 'success' | 'error' | 'warning', message: string } | null = null;
  deleteDialogRef: any = null;
  deleteTarget: Seccion | null = null;
  search = '';
  activos = true;
  page = 1;
  pageSize = 10;
  total = 0;

  constructor(private dialog: MatDialog, private authService: AuthService) {}

  ngOnInit() {
    this.cargarGradosYSecciones();
  }

  cargarGradosYSecciones() {
    // Ya no es necesario cargar grados aquí, solo secciones
    this.loadSecciones();
  }

  loadSecciones() {
    const params: any = {
      activo: this.activos,
      page: this.page,
      page_size: this.pageSize
    };
    if (this.search) params.search = this.search;
    this.authService.getSeccionesPaginated(params).subscribe({
      next: (resp: any) => {
        if (Array.isArray(resp)) {
          this.secciones = resp;
          this.total = resp.length;
        } else if (resp && Array.isArray(resp.results)) {
          this.secciones = resp.results;
          this.total = resp.count;
        } else {
          this.secciones = [];
          this.total = 0;
        }
      },
      error: (err: any) => {
        this.showAlert('error', 'Error al cargar secciones.');
      }
    });
  }

  onToggleActivos(event: any) {
    this.activos = event.value;
    this.page = 1;
    this.loadSecciones();
  }

  onSearchChange(event: any) {
    const value = event && event.target ? event.target.value : event;
    this.search = value;
    this.page = 1;
    this.loadSecciones();
  }

  onPageChange(event: any) {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadSecciones();
  }

  openAddSeccion() {
    const dialogRef = this.dialog.open(SeccionFormDialogComponent, {
      width: '400px',
      data: {}
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        this.authService.addSeccion(result).subscribe({
          next: () => {
            this.showAlert('success', 'Sección agregada correctamente');
            this.loadSecciones();
          },
          error: () => this.showAlert('error', 'Error al agregar sección')
        });
      }
    });
  }

  openEditSeccion(seccion: Seccion) {
    const dialogRef = this.dialog.open(SeccionFormDialogComponent, {
      width: '400px',
      data: { seccion }
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        this.authService.updateSeccion(seccion.id!, result).subscribe({
          next: () => {
            this.showAlert('success', 'Sección editada correctamente');
            this.loadSecciones();
          },
          error: () => this.showAlert('error', 'Error al editar sección')
        });
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
    this.authService.deleteSeccion(seccion.id!).subscribe({
      next: () => {
        this.showAlert('warning', 'Sección desactivada');
        this.loadSecciones();
      },
      error: () => this.showAlert('error', 'Error al desactivar sección')
    });
  }

  reactivarSeccion(seccion: Seccion) {
    this.authService.reactivarSeccion(seccion.id!).subscribe({
      next: () => {
        this.showAlert('success', 'Sección reactivada correctamente');
        this.loadSecciones();
      },
      error: () => this.showAlert('error', 'No se pudo reactivar la sección')
    });
  }

  showAlert(type: 'success' | 'error' | 'warning', message: string) {
    this.alert = { type, message };
    setTimeout(() => this.alert = null, 3000);
  }
}
