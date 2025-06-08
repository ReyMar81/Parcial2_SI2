// Componente de confirmación de borrado para tutor, copia adaptada de delete-confirm-dialog.component.ts
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-delete-tutor-confirm-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatIconModule],
  template: `
    <div class="w-full max-w-lg md:max-w-xl p-0 sm:p-6 flex flex-col gap-6 bg-white dark:bg-[#232a3a] rounded-2xl shadow-lg items-center">
      <mat-icon class="text-5xl text-yellow-500 bg-yellow-100 dark:bg-yellow-900 rounded-full p-2 mb-2">person_off</mat-icon>
      <h3 class="text-2xl font-bold text-center text-yellow-600 dark:text-yellow-300">¿Desactivar Tutor?</h3>
      <p class="text-center text-gray-700 dark:text-gray-200">
        ¿Estás seguro de que deseas desactivar al tutor
        <span class="font-semibold text-blue-700 dark:text-blue-300">"{{ data.nombre }}"</span>? Podrás reactivarlo más adelante.
      </p>
      <div class="flex gap-4 mt-2 w-full justify-center">
        <button mat-stroked-button color="primary" (click)="onCancel()" class="dark:text-blue-200">Cancelar</button>
        <button mat-flat-button color="warn" (click)="onDelete()" class="dark:text-blue-200">Desactivar</button>
      </div>
    </div>
  `
})
export class DeleteTutorConfirmDialogComponent {
  constructor(
    private dialogRef: MatDialogRef<DeleteTutorConfirmDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { nombre: string, desactivar?: boolean }
  ) {}

  onCancel() {
    this.dialogRef.close(false);
  }
  onDelete() {
    this.dialogRef.close(true);
  }
}
