import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { AsignacionFormDialogComponent } from './asignacion-form-dialog.component';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../../auth.service';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { FormsModule } from '@angular/forms';

export interface Asignacion {
  id: number;
  ciclo: string;
  materia: { id: number; nombre: string };
  maestro: { id: number; nombre: string };
  seccion_grado: { id: number; nombre: string };
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
    MatPaginatorModule,
    FormsModule
  ],
  templateUrl: './asignaciones-crud.component.html',
  styleUrls: ['./asignaciones-crud.component.css'],
})
export class AsignacionesCrudComponent {
  asignaciones: Asignacion[] = [];
  total = 0;
  page = 1;
  pageSize = 10;
  search = '';
  loading = false;
  alert: { type: 'success' | 'error' | 'warning', message: string } | null = null;

  constructor(private dialog: MatDialog, private authService: AuthService) {}

  ngOnInit() {
    this.loadAsignaciones();
  }

  loadAsignaciones() {
    this.loading = true;
    const params: any = {
      page: this.page,
      page_size: this.pageSize
    };
    if (this.search) params.search = this.search;
    this.authService.getMateriasAsignadas(params).subscribe({
      next: (resp: any) => {
        let asignacionesRaw = [];
        let total = 0;
        if (Array.isArray(resp)) {
          asignacionesRaw = resp;
          total = resp.length;
        } else if (resp && Array.isArray(resp.results)) {
          asignacionesRaw = resp.results;
          total = resp.count;
        }
        this.asignaciones = asignacionesRaw;
        this.total = total;
        this.loading = false;
      },
      error: () => {
        this.showAlert('error', 'Error al cargar asignaciones.');
        this.loading = false;
      }
    });
  }

  openAddAsignacion() {
    const dialogRef = this.dialog.open(AsignacionFormDialogComponent, {
      width: '400px',
      data: {}
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        // Si es batch (array), enviar todas
        if (Array.isArray(result)) {
          this.loading = true;
          this.authService.addMateriaAsignada(result).subscribe({
            next: () => {
              this.showAlert('success', 'Asignación(es) agregada(s) correctamente');
              this.loadAsignaciones();
              this.loading = false;
            },
            error: () => {
              this.showAlert('error', 'Error al agregar asignación.');
              this.loading = false;
            }
          });
        } else {
          // Individual
          this.loading = true;
          this.authService.addMateriaAsignada(result).subscribe({
            next: () => {
              this.showAlert('success', 'Asignación agregada correctamente');
              this.loadAsignaciones();
              this.loading = false;
            },
            error: () => {
              this.showAlert('error', 'Error al agregar asignación.');
              this.loading = false;
            }
          });
        }
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
        this.showAlert('success', 'Asignación editada correctamente');
        this.loadAsignaciones();
      }
    });
  }

  showAlert(type: 'success' | 'error' | 'warning', message: string) {
    this.alert = { type, message };
    setTimeout(() => this.alert = null, 3000);
  }

  onSearchChange(value: string) {
    this.search = value;
    this.page = 1;
    this.loadAsignaciones();
  }

  onPageChange(event: PageEvent) {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadAsignaciones();
  }
}
