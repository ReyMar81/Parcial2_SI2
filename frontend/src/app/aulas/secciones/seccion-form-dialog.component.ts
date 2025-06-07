import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import {Grado, Seccion } from '../../auth.service';

@Component({
  selector: 'app-seccion-form-dialog',
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
        <mat-icon class="text-5xl text-blue-500 mb-2">view_list</mat-icon>
        <h2 class="text-2xl font-bold text-center text-blue-800 dark:text-blue-200">{{ data.seccion ? 'Editar Sección' : 'Agregar Sección' }}</h2>
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
            placeholder="Nombre de la sección"
            autocomplete="off"
          />
          <div *ngIf="form.get('nombre')?.invalid && (form.get('nombre')?.dirty || form.get('nombre')?.touched)" class="text-red-500 text-xs mt-1">
            El nombre es obligatorio
          </div>
        </div>
        <div>
          <label for="aula" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Nro de Aula<span class="text-red-500">*</span></label>
          <input
            id="aula"
            matInput
            formControlName="aula"
            required
            type="number"
            min="1"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] transition text-blue-900 dark:text-blue-100"
            placeholder="Número de aula"
            autocomplete="off"
          />
        </div>
        <div>
          <label for="capacidad_maxima" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Capacidad Máxima<span class="text-red-500">*</span></label>
          <input
            id="capacidad_maxima"
            matInput
            formControlName="capacidad_maxima"
            required
            type="number"
            min="1"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] transition text-blue-900 dark:text-blue-100"
            placeholder="Capacidad máxima de alumnos"
            autocomplete="off"
          />
        </div>
        <div>
          <label for="grado" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Grado<span class="text-red-500">*</span></label>
          <mat-form-field appearance="outline" class="w-full">
            <mat-select id="grado" formControlName="grado" required>
              <mat-option *ngFor="let grado of grados" [value]="grado.id">{{ grado.nombre }}</mat-option>
            </mat-select>
          </mat-form-field>
        </div>
        <div class="flex items-center gap-2">
          <label for="estado" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Activo</label>
          <input
            id="estado"
            type="checkbox"
            [checked]="form.get('estado')?.value === 'activa'"
            (change)="onEstadoChange($event)"
            class="ml-2"
          >
        </div>
        <div class="flex gap-4 mt-2 w-full justify-center">
          <button mat-stroked-button color="primary" type="button" (click)="onCancel()" class="dark:text-blue-200">Cancelar</button>
          <button mat-flat-button color="primary" type="submit" [disabled]="form.invalid" class="dark:text-blue-200">{{ data.seccion ? 'Guardar Cambios' : 'Agregar' }}</button>
        </div>
      </form>
    </div>
  `,
  styles: [``]
})
export class SeccionFormDialogComponent {
  form: FormGroup;
  grados: Grado[];
  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<SeccionFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { seccion?: Seccion, grados: Grado[] }
  ) {
    this.grados = data.grados || [];
    this.form = this.fb.group({
      nombre: [data.seccion?.nombre || '', Validators.required],
      aula: [data.seccion?.aula ?? '', [Validators.required, Validators.min(1)]],
      capacidad_maxima: [data.seccion?.capacidad_maxima || '', [Validators.required, Validators.min(1)]],
      estado: [data.seccion?.estado ? (data.seccion.estado === 'activa' ? 'activa' : 'cerrada') : 'activa'],
      grado: [data.seccion?.grado ? (typeof data.seccion.grado === 'object' ? data.seccion.grado.id : data.seccion.grado) : '', Validators.required]
    });
  }

  onEstadoChange(event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    this.form.get('estado')?.setValue(checked ? 'activa' : 'cerrada');
  }
  onCancel() {
    this.dialogRef.close();
  }
onSubmit() {
  if (this.form.valid) {
    // Normalizar por si acaso
    let formValue = { ...this.form.value };
    if (formValue.estado !== 'activa' && formValue.estado !== 'cerrada') {
      formValue.estado = formValue.estado ? 'activa' : 'cerrada';
    }
    this.dialogRef.close(formValue);
  }
}

}
