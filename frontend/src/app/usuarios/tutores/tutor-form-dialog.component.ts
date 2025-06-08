// Componente de formulario para crear/editar tutor, copia adaptada de maestro-form-dialog.component.ts
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule, MatDialog } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule, MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { AuthService, TutorResponse, TutorCreate, AlumnoResponse } from '../../auth.service';
import { TutorCredencialesDialogComponent } from './tutor-credenciales-dialog.component';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { Observable, map, startWith } from 'rxjs';
import { AlumnoFormDialogComponent } from '../alumnos/alumnos-form-dialog.component';
import { MatListModule } from '@angular/material/list';

@Component({
  selector: 'app-tutor-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    MatSelectModule,
    MatOptionModule,
    MatDatepickerModule,
    MatNativeDateModule,
    ReactiveFormsModule,
    TutorCredencialesDialogComponent,
    MatAutocompleteModule,
    AlumnoFormDialogComponent,
    MatListModule
  ],
template: `
  <div class="w-full max-w-2xl p-0 sm:p-8 bg-white dark:bg-[#232a3a] rounded-2xl shadow-lg transition-all duration-300">
    <div class="flex flex-col items-center mb-4">
      <mat-icon class="text-5xl text-blue-500 mb-2">person</mat-icon>
      <h2 class="text-2xl font-bold text-center text-blue-800 dark:text-blue-200">
        {{ data.isEdit ? 'Editar Tutor' : 'Agregar Tutor' }}
      </h2>
    </div>
    <form [formGroup]="form" (ngSubmit)="onSubmit()" class="grid grid-cols-1 md:grid-cols-2 gap-6" autocomplete="off">
      <!-- Primera columna -->
      <div class="flex flex-col gap-4">
        <div>
          <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Nombre <span class="text-red-500">*</span></label>
          <input matInput formControlName="nombre" required placeholder="Nombre"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] text-blue-900 dark:text-blue-100"/>
        </div>
        <div>
          <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Apellido Paterno <span class="text-red-500">*</span></label>
          <input matInput formControlName="apellido_paterno" required placeholder="Apellido Paterno"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] text-blue-900 dark:text-blue-100"/>
        </div>
        <div>
          <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Apellido Materno</label>
          <input matInput formControlName="apellido_materno" placeholder="Apellido Materno"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] text-blue-900 dark:text-blue-100"/>
        </div>
        <div>
          <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Género <span class="text-red-500">*</span></label>
          <mat-select formControlName="genero" required
            class="w-full rounded-lg bg-blue-50 dark:bg-[#232531] text-blue-900 dark:text-blue-100">
            <mat-option value="M">Masculino</mat-option>
            <mat-option value="F">Femenino</mat-option>
          </mat-select>
        </div>
      </div>
      <!-- Segunda columna -->
      <div class="flex flex-col gap-4">
        <div>
          <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">CI <span class="text-red-500">*</span></label>
          <input matInput formControlName="ci" required placeholder="Carnet de identidad"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] text-blue-900 dark:text-blue-100"/>
        </div>
        <div>
          <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Dirección</label>
          <input matInput formControlName="direccion" placeholder="Dirección"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] text-blue-900 dark:text-blue-100"/>
        </div>
        <div>
          <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Contacto</label>
          <input matInput formControlName="contacto" placeholder="Teléfono o celular"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] text-blue-900 dark:text-blue-100"/>
        </div>
        <div>
          <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Fecha de Nacimiento <span class="text-red-500">*</span></label>
          <input matInput [matDatepicker]="picker" formControlName="fecha_nacimiento" required placeholder="YYYY-MM-DD"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] text-blue-900 dark:text-blue-100"/>
          <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
          <mat-datepicker #picker></mat-datepicker>
        </div>
        <div>
          <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Ocupación <span class="text-red-500">*</span></label>
          <input matInput formControlName="ocupacion" required placeholder="Ocupación"
            class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] text-blue-900 dark:text-blue-100"/>
        </div>
      </div>
      <!-- BLOQUE ASOCIAR ALUMNOS -->
      <div class="md:col-span-2">
        <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Alumnos asociados <span class="text-red-500">*</span></label>
        <mat-form-field appearance="fill" class="w-full">
          <mat-label>Buscar alumno</mat-label>
          <input type="text" matInput [formControl]="alumnoSearchCtrl" [matAutocomplete]="auto" placeholder="Buscar por nombre o CI">
          <mat-autocomplete #auto="matAutocomplete" (optionSelected)="addAlumno($event.option.value)">
            <mat-option *ngFor="let alumno of filteredAlumnos | async" [value]="alumno">
              {{ alumno.persona.nombre }} {{ alumno.persona.apellido_paterno }} {{ alumno.persona.apellido_materno }} ({{ alumno.persona.ci }})
            </mat-option>
          </mat-autocomplete>
        </mat-form-field>
        <!-- Aquí va el cuadro de alumnos asociados -->
        <div *ngIf="alumnosAsociados.length > 0" class="mt-2 bg-blue-50 dark:bg-blue-900 rounded-lg p-2">
          <div class="text-xs text-gray-500 mb-1">Alumnos asociados:</div>
          <div class="flex flex-wrap gap-2">
            <span *ngFor="let alumno of alumnosAsociados"
                  class="inline-flex items-center bg-blue-200 dark:bg-blue-800 text-blue-900 dark:text-blue-100 rounded-full px-3 py-1">
              {{ alumno.persona.nombre }} {{ alumno.persona.apellido_paterno }} {{ alumno.persona.apellido_materno }} ({{ alumno.persona.ci }})
              <button type="button"
                      (click)="removeAlumno(alumno)"
                      class="ml-2 text-red-500 hover:text-red-700 focus:outline-none">
                <mat-icon fontIcon="cancel" inline style="font-size:16px"></mat-icon>
              </button>
            </span>
          </div>
        </div>
      </div>
      <!-- BOTONES -->
      <div class="md:col-span-2 flex gap-4 mt-4 w-full justify-center">
        <button mat-stroked-button color="primary" type="button" (click)="onCancel()" class="dark:text-blue-200">Cancelar</button>
        <button mat-flat-button color="primary" type="submit" [disabled]="form.invalid || alumnosAsociados.length === 0" class="dark:text-blue-200">
          {{ data.isEdit ? 'Actualizar' : 'Agregar' }}
        </button>
      </div>
    </form>
  </div>
`
})
export class TutorFormDialogComponent {
  form: FormGroup;
  alumnos: AlumnoResponse[] = [];
  alumnosAsociados: AlumnoResponse[] = [];
  alumnoSearchCtrl!: any; // Inicializar en el constructor
  filteredAlumnos: Observable<AlumnoResponse[]> = new Observable();

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<TutorFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { tutor?: TutorResponse, isEdit?: boolean },
    private authService: AuthService,
    private dialog: MatDialog
  ) {
    this.form = this.fb.group({
      nombre: [data.tutor?.persona?.nombre || '', Validators.required],
      apellido_paterno: [data.tutor?.persona?.apellido_paterno || '', Validators.required],
      apellido_materno: [data.tutor?.persona?.apellido_materno || ''],
      genero: [data.tutor?.persona?.genero || '', Validators.required],
      ci: [data.tutor?.persona?.ci || '', Validators.required],
      direccion: [data.tutor?.persona?.direccion || ''],
      contacto: [data.tutor?.persona?.contacto || ''],
      fecha_nacimiento: [
        data.tutor?.persona?.fecha_nacimiento
          ? this.parseDate(data.tutor.persona.fecha_nacimiento)
          : null,
        Validators.required
      ],
      ocupacion: [data.tutor?.ocupacion || '', Validators.required]
    });
    this.alumnoSearchCtrl = this.fb.control('');
    this.authService.getAlumnos(true).subscribe(alumnos => {
      this.alumnos = alumnos;
      // Inicializar asociados si es edición
      if (data.isEdit && data.tutor?.alumnos_asociados) {
        // ASIGNA DIRECTAMENTE los que vienen del backend
        this.alumnosAsociados = data.tutor.alumnos_asociados;
      }
      this.setupAlumnoFilter();
    });
  }

  setupAlumnoFilter() {
    this.filteredAlumnos = this.alumnoSearchCtrl.valueChanges.pipe(
      startWith(''),
      map(value => this._filterAlumnos(typeof value === 'string' ? value : ''))
    );
  }

  private _filterAlumnos(value: string): AlumnoResponse[] {
    const filterValue = value.toLowerCase();
    return this.alumnos.filter(alumno =>
      !this.alumnosAsociados.some(a => a.id === alumno.id) &&
      (`${alumno.persona.nombre} ${alumno.persona.apellido_paterno} ${alumno.persona.apellido_materno} ${alumno.persona.ci}`.toLowerCase().includes(filterValue))
    );
  }

  addAlumno(alumno: AlumnoResponse) {
    if (!this.alumnosAsociados.some(a => a.id === alumno.id)) {
      this.alumnosAsociados.push(alumno);
      this.alumnoSearchCtrl.setValue('');
    }
  }

  removeAlumno(alumno: AlumnoResponse) {
    this.alumnosAsociados = this.alumnosAsociados.filter(a => a.id !== alumno.id);
  }

  parseDate(dateString: string): Date | null {
    if (!dateString) return null;
    const parts = dateString.split('-');
    if (parts.length !== 3) return null;
    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1;
    const day = parseInt(parts[2], 10);
    return new Date(year, month, day);
  }

  onCancel() {
    this.dialogRef.close();
  }

  onSubmit() {
    if (this.form.valid && this.alumnosAsociados.length > 0) {
      const personaData: any = {
        nombre: this.form.value.nombre,
        apellido_paterno: this.form.value.apellido_paterno,
        apellido_materno: this.form.value.apellido_materno,
        genero: this.form.value.genero,
        ci: this.form.value.ci,
        direccion: this.form.value.direccion,
        contacto: this.form.value.contacto,
        fecha_nacimiento: this.form.value.fecha_nacimiento
          ? this.form.value.fecha_nacimiento.toISOString().split('T')[0]
          : ''
      };
      if (this.data.isEdit && this.data.tutor?.persona?.id) {
        personaData.id = this.data.tutor.persona.id;
      }
      const tutorData: TutorCreate = {
        persona: personaData,
        ocupacion: this.form.value.ocupacion
      };
      const alumnosSeleccionados = this.alumnosAsociados.map(a => a.id);
      if (this.data.isEdit && this.data.tutor?.id) {
        this.authService.updateTutor(this.data.tutor.id, tutorData).subscribe({
          next: (response: any) => {
            this.authService.actualizarAlumnosTutor(this.data.tutor!.id, alumnosSeleccionados).subscribe(() => {
              this.dialogRef.close(response);
            });
          }
        });
      } else {
        this.authService.addTutor(tutorData).subscribe({
          next: (response: any) => {
            // Relacionar todos los alumnos seleccionados con el nuevo tutor
            if (response.tutor && response.tutor.id) {
              this.authService.actualizarAlumnosTutor(response.tutor.id, alumnosSeleccionados).subscribe(() => {
                this.dialogRef.close();
                this.dialog.open(TutorCredencialesDialogComponent, {
                  width: '400px',
                  data: {
                    tutor: {
                      username: response.tutor.username,
                      password: response.tutor.password
                    }
                  }
                });
              });
            } else {
              this.dialogRef.close();
            }
          }
        });
      }
    }
  }

  abrirPerfilAlumno(alumno: AlumnoResponse) {
    this.dialog.open(AlumnoFormDialogComponent, {
      width: '700px',
      data: { alumno, isEdit: false },
      disableClose: false
    });
  }
}
