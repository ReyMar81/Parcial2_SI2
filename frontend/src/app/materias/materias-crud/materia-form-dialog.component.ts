import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

export interface Materia {
  id: number;
  nombre: string;
  descripcion?: string;
}

@Component({
  selector: 'app-materia-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <div class="w-full max-w-lg md:max-w-xl p-0 sm:p-6 flex flex-col gap-6 bg-white dark:bg-[#232a3a] rounded-2xl shadow-lg">
      <div class="flex flex-col items-center mb-2">
        <mat-icon class="text-5xl text-blue-500 mb-2">bookmark</mat-icon>
        <h2 class="text-2xl font-bold text-center text-blue-800 dark:text-blue-200">{{ data.materia ? 'Editar Materia' : 'Agregar Materia' }}</h2>
      </div>
      <form [formGroup]="form" (ngSubmit)="onSubmit()" class="flex flex-col gap-5">
        <div>
          <label for="nombre" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Nombre<span class="text-red-500">*</span></label>
          <input
            id="nombre"
            matInput
            formControlName="nombre"
            required
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] transition text-blue-900 dark:text-blue-100"
            placeholder="Nombre de la materia"
            autocomplete="off"
          />
          <div *ngIf="form.get('nombre')?.invalid && (form.get('nombre')?.dirty || form.get('nombre')?.touched)" class="text-red-500 text-xs mt-1">
            El nombre es obligatorio
          </div>
        </div>
        <div>
          <label for="descripcion" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Descripción</label>
          <textarea
            id="descripcion"
            matInput
            formControlName="descripcion"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] transition text-blue-900 dark:text-blue-100"
            placeholder="Descripción de la materia"
            rows="3"
          ></textarea>
        </div>
        <div class="flex justify-end gap-4">
          <button
            mat-button
            (click)="onNoClick()"
            class="w-full sm:w-auto rounded-lg px-4 py-2 bg-gray-200 dark:bg-[#2c2f3e] text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-[#3a3d4f] transition"
          >
            Cancelar
          </button>
          <button
            mat-raised-button
            type="submit"
            class="w-full sm:w-auto rounded-lg px-4 py-2 bg-blue-600 dark:bg-blue-700 text-white hover:bg-blue-700 dark:hover:bg-blue-800 transition"
          >
            Guardar
          </button>
        </div>
      </form>
    </div>
  `
})
export class MateriaFormDialogComponent {
  form: FormGroup;

  constructor(
    public dialogRef: MatDialogRef<MateriaFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { materia: Materia },
    private fb: FormBuilder
  ) {
    this.form = this.fb.group({
      nombre: ['', Validators.required],
      descripcion: ['']
    });

    if (data.materia) {
      this.form.patchValue(data.materia);
    }
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  onSubmit(): void {
    if (this.form.valid) {
      this.dialogRef.close(this.form.value);
    }
  }
}
