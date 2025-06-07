import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { SeccionFormDialogComponent } from './seccion-form-dialog.component';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { DeleteSeccionConfirmDialogComponent } from './delete-seccion-confirm-dialog.component';
import { AuthService, Grado, Seccion } from '../../auth.service'; // <-- ESTA ES LA BUENA

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
export class SeccionesCrudComponent implements OnInit {
  secciones: Seccion[] = [];
  grados: Grado[] = [];
  alert: { type: 'success' | 'error' | 'warning', message: string } | null = null;
  deleteDialogRef: any = null;
  deleteTarget: Seccion | null = null;

  constructor(private dialog: MatDialog, private authService: AuthService) {}

  ngOnInit() {
    this.cargarGrados();
    this.cargarSecciones();
  }

  cargarGrados() {
    this.authService.getGrados().subscribe({
      next: (data) => this.grados = data,
      error: () => this.showAlert('error', 'Error al cargar grados.')
    });
  }

  cargarSecciones() {
    this.authService.getSecciones().subscribe({
      next: (data) => this.secciones = data,
      error: () => this.showAlert('error', 'Error al cargar secciones.')
    });
  }

  openAddSeccion() {
    const dialogRef = this.dialog.open(SeccionFormDialogComponent, {
      width: '400px',
      data: { grados: this.grados }
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        this.authService.addSeccion(result).subscribe({
          next: () => {
            this.showAlert('success', 'Sección agregada correctamente');
            this.cargarSecciones();
          },
          error: () => this.showAlert('error', 'Error al agregar sección')
        });
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
        // Este PUT actualiza todos los campos, incluido "estado"
        this.authService.updateSeccion(seccion.id, result).subscribe({
          next: () => {
            this.showAlert('success', 'Sección editada correctamente');
            this.cargarSecciones();
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
    this.authService.deleteSeccion(seccion.id).subscribe({
      next: () => {
        this.showAlert('warning', 'Sección eliminada');
        this.cargarSecciones();
      },
      error: () => this.showAlert('error', 'Error al eliminar sección')
    });
  }

  desactivarSeccion(seccion: Seccion) {
    this.authService.desactivarSeccion(seccion.id).subscribe({
      next: () => {
        this.showAlert('warning', 'Sección desactivada');
        this.cargarSecciones();
      },
      error: () => this.showAlert('error', 'Error al desactivar sección')
    });
  }

  showAlert(type: 'success' | 'error' | 'warning', message: string) {
    this.alert = { type, message };
    setTimeout(() => this.alert = null, 3000);
  }
  getNombreGrado(gradoRef: number | Grado): string {
  const id = typeof gradoRef === 'object' ? gradoRef.id : gradoRef;
  const grado = this.grados.find(g => g.id === id);
  return grado ? grado.nombre : '—';
}

}
