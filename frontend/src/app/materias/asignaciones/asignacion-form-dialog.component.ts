import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';

export interface Asignacion {
  id?: number;
  ciclo: string;
  materia: string;
  maestro: string;
  seccion: string;
  horas_semanales: number;
}

@Component({
  selector: 'app-asignacion-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule
  ],
  template: `
    <div class="w-full max-w-lg md:max-w-xl p-0 sm:p-6 flex flex-col gap-6 bg-white dark:bg-[#232a3a] rounded-2xl shadow-lg">
      <div class="flex flex-col items-center mb-2">
        <mat-icon class="text-5xl text-blue-500 mb-2">assignment</mat-icon>
        <h2 class="text-2xl font-bold text-center text-blue-800 dark:text-blue-200">
          {{ data.asignacion ? 'Editar Asignación' : 'Agregar Asignación' }}
        </h2>
      </div>
      <form [formGroup]="form" (ngSubmit)="onSubmit()" class="flex flex-col gap-5">
        <div>
          <label for="ciclo" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Ciclo<span class="text-red-500">*</span></label>
          <mat-select id="ciclo" formControlName="ciclo" required>
            <mat-option *ngFor="let ciclo of ciclos" [value]="ciclo">{{ ciclo }}</mat-option>
          </mat-select>
          <div *ngIf="form.get('ciclo')?.invalid && (form.get('ciclo')?.dirty || form.get('ciclo')?.touched)" class="text-red-500 text-xs mt-1">
            El ciclo es obligatorio
          </div>
        </div>
        <div>
          <label for="materia" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Materia<span class="text-red-500">*</span></label>
          <mat-select id="materia" formControlName="materia" required>
            <mat-option *ngFor="let materia of materias" [value]="materia">{{ materia }}</mat-option>
          </mat-select>
          <div *ngIf="form.get('materia')?.invalid && (form.get('materia')?.dirty || form.get('materia')?.touched)" class="text-red-500 text-xs mt-1">
            La materia es obligatoria
          </div>
        </div>
        <div>
          <label for="maestro" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Maestro<span class="text-red-500">*</span></label>
          <mat-select id="maestro" formControlName="maestro" required>
            <mat-option *ngFor="let maestro of maestros" [value]="maestro">{{ maestro }}</mat-option>
          </mat-select>
          <div *ngIf="form.get('maestro')?.invalid && (form.get('maestro')?.dirty || form.get('maestro')?.touched)" class="text-red-500 text-xs mt-1">
            El maestro es obligatorio
          </div>
        </div>
        <div>
          <label for="seccion" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Sección<span class="text-red-500">*</span></label>
          <mat-select id="seccion" formControlName="seccion" required>
            <mat-option *ngFor="let seccion of secciones" [value]="seccion">{{ seccion }}</mat-option>
          </mat-select>
          <div *ngIf="form.get('seccion')?.invalid && (form.get('seccion')?.dirty || form.get('seccion')?.touched)" class="text-red-500 text-xs mt-1">
            La sección es obligatoria
          </div>
        </div>
        <div>
          <label for="horas_semanales" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Horas semanales<span class="text-red-500">*</span></label>
          <input
            id="horas_semanales"
            type="number"
            min="1"
            matInput
            formControlName="horas_semanales"
            required
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] transition text-blue-900 dark:text-blue-100"
            placeholder="Ej: 5"
            autocomplete="off"
          />
          <div *ngIf="form.get('horas_semanales')?.invalid && (form.get('horas_semanales')?.dirty || form.get('horas_semanales')?.touched)" class="text-red-500 text-xs mt-1">
            Las horas semanales son obligatorias y deben ser mayor a 0
          </div>
        </div>
        <div class="flex gap-4 mt-2 w-full justify-center">
          <button mat-stroked-button color="primary" type="button" (click)="onCancel()" class="dark:text-blue-200">Cancelar</button>
          <button mat-flat-button color="primary" type="submit" [disabled]="form.invalid" class="dark:text-blue-200">
            {{ data.asignacion ? 'Guardar Cambios' : 'Agregar' }}
          </button>
        </div>
      </form>
    </div>
  `,
  styles: [``]
})
export class AsignacionFormDialogComponent {
  form: FormGroup;
  ciclos: string[] = [];
  materias: string[] = ['Matemáticas', 'Lengua', 'Ciencias'];
  maestros: string[] = ['Juan Pérez', 'Ana Gómez', 'Carlos Ruiz'];
  secciones: string[] = ['5A', '5B', '6A'];

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<AsignacionFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { asignacion?: Asignacion }
  ) {
    // Generar ciclos de ejemplo (año actual y 5 siguientes)
    const currentYear = new Date().getFullYear();
    for (let i = 0; i < 5; i++) {
      const ciclo = `${currentYear + i}-${currentYear + i + 1}`;
      this.ciclos.push(ciclo);
    }
    this.form = this.fb.group({
      ciclo: [data.asignacion?.ciclo || '', Validators.required],
      materia: [data.asignacion?.materia || '', Validators.required],
      maestro: [data.asignacion?.maestro || '', Validators.required],
      seccion: [data.asignacion?.seccion || '', Validators.required],
      horas_semanales: [
        data.asignacion?.horas_semanales || '',
        [Validators.required, Validators.min(1)]
      ]
    });
  }
  onCancel() {
    this.dialogRef.close();
  }
  onSubmit() {
    if (this.form.valid) {
      this.dialogRef.close(this.form.value);
    }
  }
}
