import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatPaginatorModule } from '@angular/material/paginator';
import { ReactiveFormsModule } from '@angular/forms';
import { AuthService, SeccionGrado } from '../../auth.service';
import { AsignacionFormDialogComponent } from './asignacion-form-dialog.component';
import { DeleteAsignacionConfirmDialogComponent } from './delete-asignacion-confirm-dialog.component';

@Component({
  selector: 'app-asignaciones',
  templateUrl: './asignaciones.component.html',
  styleUrls: ['./asignaciones.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatIconModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatPaginatorModule,
    AsignacionFormDialogComponent,
    DeleteAsignacionConfirmDialogComponent
  ]
})
export class AsignacionesComponent implements OnInit {
  asignaciones: SeccionGrado[] = [];
  alert: { type: 'success' | 'error' | 'warning', message: string } | null = null;
  search = '';
  activos = true;
  page = 1;
  pageSize = 10;
  total = 0;
  loading = false;

  constructor(private authService: AuthService, private dialog: MatDialog) {}

  ngOnInit() {
    this.loadAsignaciones();
  }

  loadAsignaciones() {
    this.loading = true;
    const params: any = {
      activo: this.activos,
      page: this.page,
      page_size: this.pageSize
    };
    if (this.search) params.search = this.search;
    this.authService.getSeccionGrados(params).subscribe({
      next: (resp: any) => {
        if (Array.isArray(resp)) {
          this.asignaciones = resp;
          this.total = resp.length;
        } else if (resp && Array.isArray(resp.results)) {
          this.asignaciones = resp.results;
          this.total = resp.count;
        } else {
          this.asignaciones = [];
          this.total = 0;
        }
        this.loading = false;
      },
      error: () => {
        this.showAlert('error', 'Error al cargar asignaciones.');
        this.loading = false;
      }
    });
  }

  onSearchChange(value: string) {
    this.search = value;
    this.page = 1;
    this.loadAsignaciones();
  }

  onToggleActivos(event: any) {
    this.activos = event.value;
    this.page = 1;
    this.loadAsignaciones();
  }

  onPageChange(event: any) {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadAsignaciones();
  }

  openAddAsignacion() {
    const dialogRef = this.dialog.open(AsignacionFormDialogComponent, {
      width: '500px',
      data: {}
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result && result.detalles && Array.isArray(result.detalles)) {
        // Nuevo flujo: result.detalles es un array de {seccion_id, aula, capacidad_maxima}, y result.grado_id
        const grado_id = result.grado_id;
        const detalles = result.detalles;
        let pending = detalles.length;
        let success = 0;
        if (pending === 0) return;
        detalles.forEach((detalle: any) => {
          this.authService.addSeccionGrado({
            grado_id,
            seccion_id: detalle.seccion_id,
            aula: detalle.aula,
            capacidad_maxima: detalle.capacidad_maxima
          }).subscribe({
            next: () => {
              success++;
              if (--pending === 0) {
                this.showAlert('success', `Asignación${success > 1 ? 'es' : ''} agregada${success > 1 ? 's' : ''} correctamente.`);
                this.loadAsignaciones();
              }
            },
            error: () => {
              if (--pending === 0) {
                this.showAlert('error', 'Error al agregar asignación.');
                this.loadAsignaciones();
              }
            }
          });
        });
      }
    });
  }

  openEditAsignacion(asignacion: SeccionGrado) {
    const dialogRef = this.dialog.open(AsignacionFormDialogComponent, {
      width: '500px',
      data: { asignacion }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.authService.updateSeccionGrado(asignacion.id!, {
          seccion_id: result.seccion_id,
          grado_id: Array.isArray(result.grado_ids) ? result.grado_ids[0] : result.grado_ids,
          aula: result.aula,
          capacidad_maxima: result.capacidad_maxima
        }).subscribe({
          next: () => {
            this.showAlert('success', 'Asignación editada correctamente.');
            this.loadAsignaciones();
          },
          error: () => this.showAlert('error', 'Error al editar asignación.')
        });
      }
    });
  }

  openDeleteDialog(asignacion: SeccionGrado) {
    const dialogRef = this.dialog.open(DeleteAsignacionConfirmDialogComponent, {
      width: '400px',
      data: { nombre: `${asignacion.grado_nombre} - ${asignacion.seccion_nombre}` }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.authService.desactivarSeccionGrado(asignacion.id!).subscribe({
          next: () => {
            this.showAlert('warning', 'Asignación desactivada.');
            this.loadAsignaciones();
          },
          error: () => this.showAlert('error', 'No se pudo desactivar la asignación.')
        });
      }
    });
  }

  reactivarAsignacion(asignacion: SeccionGrado) {
    this.authService.reactivarSeccionGrado(asignacion.id!).subscribe({
      next: () => {
        this.showAlert('success', 'Asignación reactivada correctamente.');
        this.loadAsignaciones();
      },
      error: () => this.showAlert('error', 'No se pudo reactivar la asignación.')
    });
  }

  showAlert(type: 'success' | 'error' | 'warning', message: string) {
    this.alert = { type, message };
    setTimeout(() => (this.alert = null), 3500);
  }
}
