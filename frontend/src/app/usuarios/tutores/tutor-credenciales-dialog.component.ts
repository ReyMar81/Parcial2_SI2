// Componente de credenciales para tutor, copia adaptada de maestro-credenciales-dialog.component.ts
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-tutor-credenciales-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatIconModule],
  template: `
    <div class="p-8 rounded-2xl bg-white dark:bg-slate-800 shadow-lg flex flex-col gap-5 items-center">
      <h3 class="text-2xl font-bold text-green-700 dark:text-green-200 flex items-center gap-2">
        <mat-icon>check_circle</mat-icon>
        Tutor registrado exitosamente
      </h3>
      <div class="w-full flex flex-col items-center gap-3">
        <div>
          <div class="font-bold text-blue-700 dark:text-blue-200 mb-2">Credenciales</div>
          <div class="flex items-center gap-2">
            <span>Usuario:</span>
            <span class="font-mono">{{ data?.tutor?.username }}</span>
            <button mat-icon-button (click)="copiar(data.tutor?.username)">
              <mat-icon>content_copy</mat-icon>
            </button>
          </div>
          <div class="flex items-center gap-2 mt-1">
            <span>Contraseña:</span>
            <span class="font-mono">{{ data?.tutor?.password }}</span>
            <button mat-icon-button (click)="copiar(data.tutor?.password)">
              <mat-icon>content_copy</mat-icon>
            </button>
          </div>
        </div>
      </div>
      <button mat-stroked-button color="primary" (click)="onClose()">
        Aceptar
      </button>
    </div>
  `
})
export class TutorCredencialesDialogComponent {
  constructor(
    private dialogRef: MatDialogRef<TutorCredencialesDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  copiar(valor: string) {
    if (!valor) return;
    navigator.clipboard.writeText(valor);
  }

  onClose() {
    this.dialogRef.close();
  }
}
