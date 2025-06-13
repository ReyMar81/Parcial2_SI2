import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { AuthService } from './auth.service';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FormsModule } from '@angular/forms';
import { NgStyle, NgClass } from '@angular/common';

@Component({
  selector: 'app-prediccion-dialog',
  templateUrl: './prediccion-dialog.component.html',
  standalone: true,
  imports: [
    NgStyle,
    NgClass,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    FormsModule
  ]
})
export class PrediccionDialogComponent {
  mensaje: string = '';
  enviando = false;
  error: string | null = null;

  constructor(
    public dialogRef: MatDialogRef<PrediccionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private authService: AuthService
  ) {}

  get aprobado(): boolean {
    return this.data?.prediccion?.aprobado;
  }
  get probabilidad(): number {
    // Cambia 'probabilidad' por 'probabilidad_aprobado' para compatibilidad con backend
    return Math.round((this.data?.prediccion?.probabilidad_aprobado ?? 0) * 100);
  }

  enviarNotificacion() {
    this.enviando = true;
    this.error = null;
    // Construir mensaje personalizado con nombre, materia y probabilidad
    const nombre = `${this.data.alumno?.persona?.nombre || ''} ${this.data.alumno?.persona?.apellido_paterno || ''} ${this.data.alumno?.persona?.apellido_materno || ''}`.trim();
    const materia = this.data.materia?.nombre || '';
    const prob = this.probabilidad;
    let mensajeFinal = `${nombre}\n${materia}: ${prob}%`;
    if (this.mensaje && this.mensaje.trim().length > 0) {
      mensajeFinal += `\n${this.mensaje.trim()}`;
    }
    this.authService.enviarNotificacionAlumnoTutores({
      alumnoId: this.data.alumno.id,
      mensaje: mensajeFinal,
      titulo: 'Alerta de predicción',
      porcentaje: this.probabilidad,
      data: {
        materia_id: this.data.materia?.id,
        materia_nombre: this.data.materia?.nombre,
        tipo_nota: this.data.tipoNota,
      },
    }).subscribe({
      next: () => {
        this.enviando = false;
        this.dialogRef.close({ enviarNotificacion: true });
      },
      error: (err) => {
        this.enviando = false;
        this.error = 'Error al enviar notificación';
      }
    });
  }

  cerrar() {
    this.dialogRef.close();
  }
}
