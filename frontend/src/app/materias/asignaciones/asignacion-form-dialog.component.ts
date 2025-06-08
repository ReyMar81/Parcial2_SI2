import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { AuthService } from '../../auth.service';

export interface Asignacion {
  id?: number;
  ciclo: string;
  materia: number; // id de materia
  maestro: number; // id de maestro
  seccion_grado_ids: number[]; // para batch
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
          <input
            id="ciclo"
            type="text"
            formControlName="ciclo"
            required
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] transition text-blue-900 dark:text-blue-100"
            placeholder="Ej: 2023-2024"
            autocomplete="off"
          />
          <div *ngIf="form.get('ciclo')?.invalid && (form.get('ciclo')?.dirty || form.get('ciclo')?.touched)" class="text-red-500 text-xs mt-1">
            El ciclo es obligatorio
          </div>
        </div>
        <div>
          <label for="materia" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Materia<span class="text-red-500">*</span></label>
          <mat-select id="materia" formControlName="materia" required>
            <mat-option *ngFor="let materia of materias" [value]="materia.id">{{ materia.nombre }}</mat-option>
          </mat-select>
          <div *ngIf="form.get('materia')?.invalid && (form.get('materia')?.dirty || form.get('materia')?.touched)" class="text-red-500 text-xs mt-1">
            La materia es obligatoria
          </div>
        </div>
        <div>
          <label for="maestro" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Maestro<span class="text-red-500">*</span></label>
          <mat-select id="maestro" formControlName="maestro" required>
            <mat-option *ngFor="let maestro of maestros" [value]="maestro.id">{{ maestro.nombre }}</mat-option>
          </mat-select>
          <div *ngIf="form.get('maestro')?.invalid && (form.get('maestro')?.dirty || form.get('maestro')?.touched)" class="text-red-500 text-xs mt-1">
            El maestro es obligatorio
          </div>
        </div>
        <div>
          <label for="seccion_grado_ids" class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Secciones-Grado<span class="text-red-500">*</span></label>
          <mat-select id="seccion_grado_ids" formControlName="seccion_grado_ids" [multiple]="!isEdit" required>
            <mat-option *ngFor="let sg of seccionGrados" [value]="sg.id">{{ sg.nombre }}</mat-option>
          </mat-select>
          <div *ngIf="form.get('seccion_grado_ids')?.invalid && (form.get('seccion_grado_ids')?.dirty || form.get('seccion_grado_ids')?.touched)" class="text-red-500 text-xs mt-1">
            Debe seleccionar al menos una sección-grado
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
export class AsignacionFormDialogComponent implements OnInit {
  form: FormGroup;
  materias: any[] = [];
  maestros: any[] = [];
  seccionGrados: any[] = [];
  isEdit: boolean;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<AsignacionFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { asignacion?: any },
    private authService: AuthService
  ) {
    this.isEdit = !!data.asignacion;
    this.form = this.fb.group({
      ciclo: [data.asignacion?.ciclo || '', Validators.required],
      materia: [data.asignacion?.materia?.id || '', Validators.required],
      maestro: [data.asignacion?.maestro?.id || '', Validators.required],
      seccion_grado_ids: [data.asignacion ? [data.asignacion.seccion_grado?.id] : [], Validators.required],
      horas_semanales: [data.asignacion?.horas_semanales || '', [Validators.required, Validators.min(1)]]
    });
  }

  ngOnInit() {
    // Materias activas (respuesta paginada)
    this.authService.getMaterias().subscribe((resp: any) => {
      const mats = Array.isArray(resp) ? resp : (resp.results ?? []);
      this.materias = mats.filter((m: any) => m.activo);
    });
    // Maestros activos (respuesta paginada)
    this.authService.getMaestros().subscribe((resp: any) => {
      const maes = Array.isArray(resp) ? resp : (resp.results ?? []);
      this.maestros = maes.filter((m: any) => m.persona && (m.activo === undefined || m.activo)).map((m: any) => ({
        id: m.id,
        nombre: m.persona.nombre + ' ' + m.persona.apellido_paterno + (m.persona.apellido_materno ? (' ' + m.persona.apellido_materno) : '')
      }));
    });
    // Secciones-grado activas (respuesta paginada)
    this.authService.getSeccionGrados().subscribe((resp: any) => {
      const arr = Array.isArray(resp) ? resp : (resp.results ?? []);
      let activos = arr.filter((sg: any) => sg.activo).map((sg: any) => ({
        id: Number(sg.id),
        nombre: `${sg.grado_nombre} - ${sg.seccion_nombre} (${sg.aula})`
      }));
      if (this.isEdit && this.data.asignacion?.seccion_grado) {
        const actual = this.data.asignacion.seccion_grado;
        const actualId = Number(actual.id);
        if (!activos.some((sg: {id: number, nombre: string}) => sg.id === actualId)) {
          let nombre = actual.nombre;
          if (!nombre) {
            nombre = `${actual.grado_nombre || ''} - ${actual.seccion_nombre || ''} (${actual.aula || ''})`.replace(/^- | - \(\)/, '').trim();
            if (!nombre || nombre === '- ()') nombre = `ID ${actualId}`;
          }
          activos = [
            { id: actualId, nombre },
            ...activos
          ];
        }
        this.seccionGrados = activos;
        // Forzar el valor seleccionado en el form después de cargar las opciones
        setTimeout(() => {
          this.form.get('seccion_grado_ids')?.setValue([actualId]);
        }, 0);
      } else {
        this.seccionGrados = activos;
      }
    });
  }

  onCancel() {
    this.dialogRef.close();
  }

  onSubmit() {
    if (this.form.valid) {
      const value = this.form.value;
      if (this.isEdit) {
        // Edición: solo un id
        const payload = {
          ciclo: value.ciclo,
          materia: value.materia,
          maestro: value.maestro,
          seccion_grado_id: value.seccion_grado_ids[0],
          horas_semanales: value.horas_semanales
        };
        this.dialogRef.close(payload);
      } else {
        // Creación: batch, usar seccion_grado_id
        const batch = value.seccion_grado_ids.map((sgid: number) => ({
          ciclo: value.ciclo,
          materia: value.materia,
          maestro: value.maestro,
          seccion_grado_id: sgid,
          horas_semanales: value.horas_semanales
        }));
        this.dialogRef.close(batch);
      }
    }
  }
}
