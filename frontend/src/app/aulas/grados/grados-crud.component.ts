import { Component, OnInit } from '@angular/core';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { GradoFormDialogComponent } from './grado-form-dialog.component';
import { DeleteGradoConfirmDialogComponent } from './delete-grado-confirm-dialog.component';
import { AuthService, Grado } from '../../auth.service';

@Component({
  selector: 'app-grados-crud',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatIconModule,
    MatButtonModule,
    GradoFormDialogComponent,
    DeleteGradoConfirmDialogComponent
  ],
  templateUrl: './grados-crud.component.html',
  styleUrls: ['./grados-crud.component.css']
})
export class GradosCrudComponent implements OnInit {
  grados: Grado[] = [];
  alert: { type: string, message: string } | null = null;

  constructor(
    private authService: AuthService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadGrados();
  }

  loadGrados() {
    this.authService.getGrados().subscribe({
      next: (data) => this.grados = data,
      error: () => this.showAlert('error', 'Error al cargar grados.')
    });
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
        this.authService.deleteGrado(grado.id).subscribe({
          next: () => {
            this.showAlert('success', 'Grado eliminado.');
            this.loadGrados();
          },
          error: () => this.showAlert('error', 'No se pudo eliminar el grado.')
        });
      }
    });
  }

  showAlert(type: string, message: string) {
    this.alert = { type, message };
    setTimeout(() => { this.alert = null; }, 3000);
  }
}
