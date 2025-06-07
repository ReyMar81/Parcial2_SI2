import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService, Seccion } from '../auth.service';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common';
import { MatNativeDateModule } from '@angular/material/core';

@Component({
  selector: 'app-inscripcion-form',
  standalone: true,
    imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDatepickerModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    MatNativeDateModule
    ],
  templateUrl: './inscripcion.component.html',
  styleUrls: ['./inscripcion.component.css']
})

export class InscripcionFormComponent implements OnInit {
  form: FormGroup;
  secciones: Seccion[] = [];
  loading: boolean = false;
  successData: any = null;
  errorMsg: string | null = null;
  copyMsg: string | null = null;

  constructor(private fb: FormBuilder, private authService: AuthService) {
    console.log('CONSTRUCTOR InscripcionFormComponent');
    const currentYear = new Date().getFullYear().toString();
    this.form = this.fb.group({
      // Alumno
      nombre_alumno: ['', Validators.required],
      ap_paterno_alumno: ['', Validators.required],
      ap_materno_alumno: ['', Validators.required],
      genero_alumno: ['', Validators.required],
      ci_alumno: ['', Validators.required],
      direccion_alumno: [''],
      contacto_alumno: [''],
      fecha_nacimiento_alumno: ['', Validators.required],
      // Tutor
      nombre_tutor: ['', Validators.required],
      ap_paterno_tutor: ['', Validators.required],
      ap_materno_tutor: ['', Validators.required],
      genero_tutor: ['', Validators.required],
      ci_tutor: ['', Validators.required],
      direccion_tutor: [''],
      contacto_tutor: [''],
      fecha_nacimiento_tutor: ['', Validators.required],
      ocupacion_tutor: [''],
      // Otros
      tipo_relacion: ['', Validators.required],
      seccion_id: ['', Validators.required],
      ciclo: [currentYear, Validators.required]
    });
  }

  ngOnInit(): void {
    console.log('ngOnInit InscripcionFormComponent');
    this.authService.getSecciones().subscribe({
      next: (secciones: Seccion[]) => {
        console.log('SECCIONES CARGADAS:', secciones);
        this.secciones = secciones.filter((s: Seccion) => s.estado === 'activa');
      },
      error: () => this.errorMsg = 'No se pudieron cargar las secciones.'
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.errorMsg = null;
    const values = this.form.value;
    const inscripcionPayload = {
      alumno: {
        nombre: values.nombre_alumno,
        apellido_paterno: values.ap_paterno_alumno,
        apellido_materno: values.ap_materno_alumno,
        genero: values.genero_alumno,
        ci: values.ci_alumno,
        direccion: values.direccion_alumno,
        contacto: values.contacto_alumno,
        fecha_nacimiento: this.formatFecha(values.fecha_nacimiento_alumno)
      },
      tutor: {
        nombre: values.nombre_tutor,
        apellido_paterno: values.ap_paterno_tutor,
        apellido_materno: values.ap_materno_tutor,
        genero: values.genero_tutor,
        ci: values.ci_tutor,
        direccion: values.direccion_tutor,
        contacto: values.contacto_tutor,
        fecha_nacimiento: this.formatFecha(values.fecha_nacimiento_tutor),
        ocupacion: values.ocupacion_tutor
      },
      tipo_relacion: values.tipo_relacion,
      seccion_id: values.seccion_id,
      ciclo: values.ciclo
    };

    this.authService.inscribirAlumno(inscripcionPayload).subscribe({
      next: (resp: any) => {
        this.loading = false;
        this.successData = resp;
        this.form.reset({ ciclo: new Date().getFullYear().toString() });
      },
      error: (err: any) => {
        this.loading = false;
        this.errorMsg = err?.error?.mensaje || 'Ocurrió un error al inscribir.';
      }
    });
  }

  formatFecha(fecha: any): string {
    if (!fecha) return '';
    if (typeof fecha === 'string') return fecha.slice(0, 10);
    const d = new Date(fecha);
    return d.toISOString().slice(0, 10);
  }

  copiar(valor: string) {
    if (!valor) return;
    navigator.clipboard.writeText(valor).then(() => {
      this.copyMsg = 'Copiado!';
      setTimeout(() => this.copyMsg = null, 1200);
    }).catch(() => {
      alert('No se pudo copiar al portapapeles');
    });
  }
}
