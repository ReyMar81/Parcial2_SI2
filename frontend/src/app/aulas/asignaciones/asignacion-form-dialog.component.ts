import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormArray } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { AuthService, Grado, Seccion, SeccionGrado } from '../../auth.service';
import { OnInit } from '@angular/core';

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
        <mat-icon class="text-5xl text-blue-500 mb-2">link</mat-icon>
        <h2 class="text-2xl font-bold text-center text-blue-800 dark:text-blue-200">{{ data.asignacion ? 'Editar Asignación' : 'Nueva Asignación' }}</h2>
      </div>
      <form [formGroup]="form" (ngSubmit)="onSubmit()" class="flex flex-col gap-5">
        <div *ngIf="secciones.length === 0 || grados.length === 0" class="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded mb-2">
          <div *ngIf="secciones.length === 0">No hay secciones activas disponibles. Por favor, cree o active una sección antes de continuar.</div>
          <div *ngIf="grados.length === 0">No hay grados activos disponibles. Por favor, cree o active un grado antes de continuar.</div>
        </div>
        <div *ngIf="advertencias.length > 0" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded mb-2">
          <div *ngFor="let adv of advertencias">{{ adv }}</div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <ng-container *ngIf="!data.asignacion; else soloLectura">
            <div>
              <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Grado<span class="text-red-500">*</span></label>
              <mat-form-field appearance="fill" class="w-full">
                <mat-select formControlName="grado_id" required [disabled]="grados.length === 0">
                  <mat-option *ngFor="let grado of grados" [value]="grado.id">{{ grado.nombre }}</mat-option>
                </mat-select>
              </mat-form-field>
            </div>
            <div>
              <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Secciones<span class="text-red-500">*</span></label>
              <mat-form-field appearance="fill" class="w-full">
                <mat-select formControlName="seccion_ids" multiple required [disabled]="secciones.length === 0">
                  <mat-option *ngFor="let seccion of secciones" [value]="seccion.id">{{ seccion.nombre }}</mat-option>
                </mat-select>
              </mat-form-field>
            </div>
          </ng-container>
          <ng-template #soloLectura>
            <div>
              <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Grado</label>
              <div class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border border-blue-200 dark:border-blue-700 text-blue-900 dark:text-blue-100">{{ gradoNombre }}</div>
            </div>
            <div>
              <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Sección</label>
              <div class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border border-blue-200 dark:border-blue-700 text-blue-900 dark:text-blue-100">{{ seccionNombre }}</div>
            </div>
          </ng-template>
        </div>
        <div formArrayName="seccionDetalles" class="grid grid-cols-1 gap-4">
          <div *ngFor="let detalle of seccionDetalles.controls; let i = index" [formGroupName]="i" class="p-4 bg-blue-50 dark:bg-[#232531] rounded-lg shadow">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Aula<span class="text-red-500">*</span></label>
                <input matInput formControlName="aula" required placeholder="Aula" class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none" />
              </div>
              <div>
                <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Capacidad Máxima<span class="text-red-500">*</span></label>
                <input matInput type="number" formControlName="capacidad_maxima" required min="1" placeholder="Capacidad" class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none" />
              </div>
            </div>
          </div>
        </div>
        <div class="flex gap-4 mt-2 w-full justify-center">
          <button mat-stroked-button color="primary" type="button" (click)="onCancel()" class="dark:text-blue-200">Cancelar</button>
          <button mat-flat-button color="primary" type="submit" [disabled]="form.invalid || secciones.length === 0 || grados.length === 0 || advertencias.length > 0" class="dark:text-blue-200">{{ data.asignacion ? 'Guardar Cambios' : 'Agregar' }}</button>
        </div>
      </form>
    </div>
  `
})
export class AsignacionFormDialogComponent implements OnInit {
  form: FormGroup;
  grados: Grado[] = [];
  secciones: Seccion[] = [];
  asignacionesExistentes: SeccionGrado[] = [];
  advertencias: string[] = [];

  get seccionDetalles(): FormArray {
    return this.form.get('seccionDetalles') as FormArray;
  }

  get gradoNombre(): string {
    if (!this.data.asignacion) return '';
    // Buscar por id numérico o string (por si acaso)
    const grado = this.grados.find(g => g.id == this.data.asignacion!.grado_id);
    return grado ? grado.nombre : String(this.data.asignacion.grado_nombre || this.data.asignacion.grado_id);
  }
  get seccionNombre(): string {
    if (!this.data.asignacion) return '';
    const seccion = this.secciones.find(s => s.id == this.data.asignacion!.seccion_id);
    return seccion ? seccion.nombre : String(this.data.asignacion.seccion_nombre || this.data.asignacion.seccion_id);
  }

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<AsignacionFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { asignacion?: SeccionGrado },
    private authService: AuthService
  ) {
    // Cambia el formulario para el nuevo flujo
    this.form = this.fb.group({
      grado_id: [null, Validators.required],
      seccion_ids: [[], Validators.required],
      seccionDetalles: this.fb.array([]) // [{seccion_id, aula, capacidad_maxima}]
    });
  }

  ngOnInit() {
    // Cargar grados y secciones activas
    this.authService.getGrados(true).subscribe((resp: any) => {
      this.grados = resp && Array.isArray(resp.results) ? resp.results : (Array.isArray(resp) ? resp : []);
      this.checkAndPatchForm();
    });
    this.authService.getSecciones(true).subscribe((resp: any) => {
      this.secciones = resp && Array.isArray(resp.results) ? resp.results : (Array.isArray(resp) ? resp : []);
      this.checkAndPatchForm();
    });
    // Cargar todas las asignaciones activas (para validación de duplicados)
    this.authService.getSeccionGrados({activo: true, page_size: 1000}).subscribe((resp: any) => {
      this.asignacionesExistentes = Array.isArray(resp) ? resp : (resp && Array.isArray(resp.results) ? resp.results : []);
    });

    // Escuchar cambios en seccion_ids para actualizar el FormArray dinámico
    this.form.get('seccion_ids')?.valueChanges.subscribe((ids: number[]) => {
      this.syncSeccionDetalles(ids);
    });
  }

  checkAndPatchForm() {
    if (this.data.asignacion) {
      // En edición: solo permite cambiar aula y capacidad, grado y sección bloqueados pero visibles
      this.form = this.fb.group({
        grado_id: [{ value: this.data.asignacion.grado_id, disabled: true }, Validators.required],
        seccion_ids: [{ value: [this.data.asignacion.seccion_id], disabled: true }, Validators.required],
        seccionDetalles: this.fb.array([
          this.fb.group({
            seccion_id: [{ value: this.data.asignacion.seccion_id, disabled: true }, Validators.required],
            aula: [this.data.asignacion.aula, Validators.required],
            capacidad_maxima: [this.data.asignacion.capacidad_maxima, [Validators.required, Validators.min(1)]]
          })
        ])
      });
    } else {
      // En creación: seleccionar un solo grado y varias secciones
      this.form.get('grado_id')?.enable();
      this.form.get('seccion_ids')?.enable();
      // Si ya hay secciones seleccionadas (por ejemplo, si el usuario vuelve atrás), sincroniza los detalles
      const ids = this.form.get('seccion_ids')?.value || [];
      this.syncSeccionDetalles(ids);
    }
  }

  syncSeccionDetalles(ids: number[]) {
    // Sincroniza el FormArray con los ids seleccionados
    const detalles = this.seccionDetalles;
    // Elimina los que ya no están
    while (detalles.length > 0) {
      detalles.removeAt(0);
    }
    ids.forEach(seccion_id => {
      detalles.push(this.fb.group({
        seccion_id: [seccion_id, Validators.required],
        aula: ['', Validators.required],
        capacidad_maxima: [1, [Validators.required, Validators.min(1)]]
      }));
    });
  }

  onSubmit() {
    this.advertencias = [];
    if (this.data.asignacion) {
      // Modo edición: solo uno, pero usando el mismo FormArray
      const raw = this.form.getRawValue();
      const grado_id = raw.grado_id;
      const detalles = raw.seccionDetalles;
      const detalle = detalles[0];
      const seccion_id = detalle.seccion_id;
      const yaExiste = this.asignacionesExistentes.some(a =>
        a.seccion_id === seccion_id && a.grado_id === grado_id &&
        (!this.data.asignacion || a.id !== this.data.asignacion.id)
      );
      if (yaExiste) {
        const grado = this.grados.find(g => g.id === grado_id)?.nombre || 'Grado';
        const seccion = this.secciones.find(s => s.id === seccion_id)?.nombre || 'Sección';
        this.advertencias.push(`Ya existe la asignación ${grado} - ${seccion}.`);
      }
      if (!detalle.aula || detalle.capacidad_maxima < 1) {
        const seccion = this.secciones.find(s => s.id === seccion_id)?.nombre || 'Sección';
        this.advertencias.push(`Debe completar todos los campos para la sección ${seccion}.`);
      }
      if (this.form.valid && this.advertencias.length === 0) {
        this.dialogRef.close({
          grado_id,
          seccion_id,
          aula: detalle.aula,
          capacidad_maxima: detalle.capacidad_maxima
        });
      }
    } else {
      // Modo creación múltiple
      const grado_id = this.form.value.grado_id;
      const detalles = this.seccionDetalles.value;
      // Validar duplicados y campos vacíos
      detalles.forEach((detalle: any) => {
        const yaExiste = this.asignacionesExistentes.some(a =>
          a.seccion_id === detalle.seccion_id && a.grado_id === grado_id
        );
        if (yaExiste) {
          const grado = this.grados.find(g => g.id === grado_id)?.nombre || 'Grado';
          const seccion = this.secciones.find(s => s.id === detalle.seccion_id)?.nombre || 'Sección';
          this.advertencias.push(`Ya existe la asignación ${grado} - ${seccion}.`);
        }
        if (!detalle.aula || detalle.capacidad_maxima < 1) {
          const seccion = this.secciones.find(s => s.id === detalle.seccion_id)?.nombre || 'Sección';
          this.advertencias.push(`Debe completar todos los campos para la sección ${seccion}.`);
        }
      });
      if (this.form.valid && this.advertencias.length === 0) {
        // Devuelve todos los detalles para que el componente padre haga las peticiones
        this.dialogRef.close({
          grado_id,
          detalles
        });
      }
    }
  }

  onCancel() {
    this.dialogRef.close();
  }
}
