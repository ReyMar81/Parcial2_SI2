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
import { AuthService, MaestroResponse, MaestroCreate } from '../../auth.service';
import { MaestroCredencialesDialogComponent } from './maestro-credenciales-dialog.component';

@Component({
  selector: 'app-maestro-form-dialog',
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
    MaestroCredencialesDialogComponent
  ],
  template: `
    <div class="w-full max-w-2xl p-0 sm:p-8 bg-white dark:bg-[#232a3a] rounded-2xl shadow-lg transition-all duration-300">
      <div class="flex flex-col items-center mb-4">
        <mat-icon class="text-5xl text-blue-500 mb-2">person</mat-icon>
        <h2 class="text-2xl font-bold text-center text-blue-800 dark:text-blue-200">
          {{ data.isEdit ? 'Editar Maestro' : 'Agregar Maestro' }}
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
            <label class="block text-gray-700 dark:text-gray-200 font-medium mb-1">Especialidad <span class="text-red-500">*</span></label>
            <input matInput formControlName="especialidad" required placeholder="Especialidad"
              class="w-full rounded-lg px-4 py-2 bg-blue-50 dark:bg-[#232531] border-none focus:ring-2 focus:ring-blue-300 focus:bg-white dark:focus:bg-[#232531] text-blue-900 dark:text-blue-100"/>
          </div>
        </div>
        <div class="md:col-span-2 flex gap-4 mt-4 w-full justify-center">
          <button mat-stroked-button color="primary" type="button" (click)="onCancel()" class="dark:text-blue-200">Cancelar</button>
          <button mat-flat-button color="primary" type="submit" [disabled]="form.invalid" class="dark:text-blue-200">
            {{ data.isEdit ? 'Actualizar' : 'Agregar' }}
          </button>
        </div>
      </form>
    </div>
  `
})
export class MaestroFormDialogComponent {
  form: FormGroup;

    constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<MaestroFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { maestro?: MaestroResponse, isEdit?: boolean },
    private authService: AuthService,
    private dialog: MatDialog 
  ) {
    this.form = this.fb.group({
      nombre: [data.maestro?.persona?.nombre || '', Validators.required],
      apellido_paterno: [data.maestro?.persona?.apellido_paterno || '', Validators.required],
      apellido_materno: [data.maestro?.persona?.apellido_materno || ''],
      genero: [data.maestro?.persona?.genero || '', Validators.required],
      ci: [data.maestro?.persona?.ci || '', Validators.required],
      direccion: [data.maestro?.persona?.direccion || ''],
      contacto: [data.maestro?.persona?.contacto || ''],
      fecha_nacimiento: [
        data.maestro?.persona?.fecha_nacimiento
          ? this.parseDate(data.maestro.persona.fecha_nacimiento)
          : null,
        Validators.required
      ],
      especialidad: [data.maestro?.especialidad || '', Validators.required]
    });
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
    if (this.form.valid) {
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

    // Agrega el id si es edición
    if (this.data.isEdit && this.data.maestro?.persona?.id) {
        personaData.id = this.data.maestro.persona.id;
    }

    const maestroData: MaestroCreate = {
        persona: personaData,
        especialidad: this.form.value.especialidad
    };

    if (this.data.isEdit && this.data.maestro?.id) {
        // EDITAR MAESTRO
        this.authService.updateMaestro(this.data.maestro.id, maestroData).subscribe({
        next: (response: any) => {
            this.dialogRef.close(response);
        }
        });
    } else {
        // CREAR MAESTRO
        this.authService.addMaestro(maestroData).subscribe({
        next: (response: any) => {
            // Cierra el form dialog actual
            this.dialogRef.close();

            // Abre el dialogo de credenciales
            this.dialog.open(MaestroCredencialesDialogComponent, {
                width: '400px',
                data: {
                    maestro: {
                        username: response.maestro.username,
                        password: response.maestro.password,
                        registro: response.maestro.registro
                    }
                }
            });
        }
        });
    }
    }
  }
}
