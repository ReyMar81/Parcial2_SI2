import { Component, OnInit } from '@angular/core';
import { AuthService, MaestroResponse } from '../../auth.service';
import { MaestroFormDialogComponent } from './maestro-form-dialog.component';
import { DeleteMaestroConfirmDialogComponent } from './delete-confirm-dialog.component';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MaestroCredencialesDialogComponent } from './maestro-credenciales-dialog.component';


@Component({
  selector: 'app-maestros',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatIconModule,
    MatButtonModule,
    MaestroFormDialogComponent,
    DeleteMaestroConfirmDialogComponent,
    MatDatepickerModule,
    MatNativeDateModule,
    MaestroCredencialesDialogComponent
  ],
  templateUrl: './maestros.component.html',
  styleUrls: ['./maestros.component.css']
})
export class MaestrosComponent implements OnInit {
  maestros: MaestroResponse[] = [];
  alert: { type: string, message: string } | null = null;

  constructor(
    private authService: AuthService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadMaestros();
  }

  loadMaestros() {
    this.authService.getMaestros().subscribe({
      next: (data: MaestroResponse[]) => this.maestros = data,
      error: () => this.showAlert('error', 'Error al cargar maestros.')
    });
  }

  openAddMaestro() {
    const dialogRef = this.dialog.open(MaestroFormDialogComponent, {
      width: '500px',
      data: { isEdit: false }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.showAlert('success', 'Maestro agregado exitosamente.');
        this.loadMaestros();
      }
    });
  }

  openEditMaestro(maestro: MaestroResponse) {
    const dialogRef = this.dialog.open(MaestroFormDialogComponent, {
      width: '500px',
      data: { maestro, isEdit: true }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.showAlert('success', 'Maestro editado exitosamente.');
        this.loadMaestros();
      }
    });
  }

  openDeleteDialog(maestro: MaestroResponse) {
    const dialogRef = this.dialog.open(DeleteMaestroConfirmDialogComponent, {
      width: '350px',
      data: { nombre: maestro.persona.nombre + ' ' + maestro.persona.apellido_paterno }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.authService.deleteMaestro(maestro.id!).subscribe({
          next: () => {
            this.showAlert('success', 'Maestro eliminado.');
            this.loadMaestros();
          },
          error: () => this.showAlert('error', 'No se pudo eliminar el maestro.')
        });
      }
    });
  }

  showAlert(type: string, message: string) {
    this.alert = { type, message };
    setTimeout(() => { this.alert = null; }, 3000);
  }
}
