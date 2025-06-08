import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-delete-seccion-confirm-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatIconModule],
  template: `
    <div class="p-6 flex flex-col gap-4 items-center bg-white dark:bg-[#232a3a] rounded-2xl shadow-lg w-full max-w-lg md:max-w-xl">
      <mat-icon class="text-6xl text-yellow-500 bg-yellow-100 dark:bg-yellow-900 rounded-full p-2 mb-2">block</mat-icon>
      <h2 class="text-xl font-bold text-center text-yellow-800 dark:text-yellow-200">¿Desactivar Sección?</h2>
      <p class="text-center text-gray-700 dark:text-gray-200">
        ¿Estás seguro de que deseas desactivar la sección <span class="font-semibold text-blue-700 dark:text-blue-300">"{{ data.nombre }}"</span>?<br>Podrás reactivarla más adelante.
      </p>
      <div class="flex gap-4 mt-2 w-full justify-center">
        <button mat-stroked-button color="primary" (click)="onCancel()" class="dark:text-blue-200">Cancelar</button>
        <button mat-flat-button color="warn" (click)="onDelete()" class="dark:text-yellow-200">Desactivar</button>
      </div>
    </div>
  `,
  styles: [``]
})
export class DeleteSeccionConfirmDialogComponent {
  constructor(
    private dialogRef: MatDialogRef<DeleteSeccionConfirmDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { nombre: string }
  ) {}

  onCancel() {
    this.dialogRef.close(false);
  }
  onDelete() {
    this.dialogRef.close(true);
  }
}
