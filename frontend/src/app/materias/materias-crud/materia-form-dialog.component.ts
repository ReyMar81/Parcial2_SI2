import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { AuthService, Materia } from '../../auth.service';

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
        <mat-icon class="text-5xl text-blue-500 mb-2">library_books</mat-icon>
        <h2 class="text-2xl font-bold text-center text-blue-800 dark:text-blue-200">
          {{ data.materia ? 'Editar Materia' : 'Agregar Materia' }}
        </h2>
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
            rows="2"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] transition text-blue-900 dark:text-blue-100"
            placeholder="Descripción de la materia (opcional)"
          ></textarea>
        </div>
        <div class="flex gap-4 mt-2 w-full justify-center">
          <button mat-stroked-button color="primary" type="button" (click)="onCancel()" class="dark:text-blue-200">Cancelar</button>
          <button mat-flat-button color="primary" type="submit" [disabled]="form.invalid" class="dark:text-blue-200">
            {{ data.materia ? 'Guardar Cambios' : 'Agregar' }}
          </button>
        </div>
      </form>
    </div>
  `
})
export class MateriaFormDialogComponent {
  form: FormGroup;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<MateriaFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { materia?: Materia },
    private authService: AuthService
  ) {
    this.form = this.fb.group({
      nombre: [data.materia?.nombre || '', Validators.required],
      descripcion: [data.materia?.descripcion || '']
    });
  }

  onCancel() {
    this.dialogRef.close();
  }

  onSubmit() {
    if (this.form.valid) {
      if (this.data.materia && this.data.materia.id) {
        this.authService.updateMateria(this.data.materia.id, this.form.value).subscribe(() => {
          this.dialogRef.close(this.form.value);
        });
      } else {
        this.authService.addMateria(this.form.value).subscribe(() => {
          this.dialogRef.close(this.form.value);
        });
      }
    }
  }
}
