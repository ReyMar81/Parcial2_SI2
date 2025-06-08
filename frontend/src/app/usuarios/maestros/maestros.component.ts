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
import { PageEvent } from '@angular/material/paginator';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatPaginatorModule } from '@angular/material/paginator';

@Component({
  selector: 'app-maestros',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatIconModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatFormFieldModule,
    MatInputModule,
    MatPaginatorModule,
    MaestroFormDialogComponent,
    MaestroCredencialesDialogComponent,
    DeleteMaestroConfirmDialogComponent,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  templateUrl: './maestros.component.html',
  styleUrls: ['./maestros.component.css']
})
export class MaestrosComponent implements OnInit {
  maestros: MaestroResponse[] = [];
  alert: { type: string, message: string } | null = null;
  activos = true;
  search = '';
  page = 1;
  pageSize = 10;
  total = 0;

  constructor(
    private authService: AuthService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadMaestros();
  }

  loadMaestros() {
    const params: any = {
      activo: this.activos,
      page: this.page,
      page_size: this.pageSize
    };
    if (this.search) params.search = this.search;
    this.authService.getMaestrosPaginated(params).subscribe({
      next: (resp: any) => {
        this.maestros = resp.results;
        this.total = resp.count;
      },
      error: () => this.showAlert('error', 'Error al cargar maestros.')
    });
  }

  onToggleActivos(activos: boolean) {
    this.activos = activos;
    this.page = 1;
    this.loadMaestros();
  }

  onSearchChange(value: string) {
    this.search = value;
    this.page = 1;
    this.loadMaestros();
  }

  onPageChange(event: PageEvent) {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadMaestros();
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

  openDeactivateDialog(maestro: MaestroResponse) {
    const dialogRef = this.dialog.open(DeleteMaestroConfirmDialogComponent, {
      width: '350px',
      data: { nombre: maestro.persona.nombre + ' ' + maestro.persona.apellido_paterno, desactivar: true }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.authService.deleteMaestro(maestro.id!).subscribe({
          next: () => {
            this.showAlert('success', 'Maestro desactivado correctamente.');
            this.loadMaestros();
          },
          error: () => this.showAlert('error', 'No se pudo desactivar el maestro.')
        });
      }
    });
  }

  reactivarMaestro(maestro: MaestroResponse) {
    this.authService.reactivarMaestro(maestro.id!).subscribe({
      next: () => {
        this.showAlert('success', 'Maestro reactivado correctamente.');
        this.loadMaestros();
      },
      error: () => this.showAlert('error', 'No se pudo reactivar el maestro.')
    });
  }

  showAlert(type: string, message: string) {
    this.alert = { type, message };
    setTimeout(() => { this.alert = null; }, 3000);
  }
}
