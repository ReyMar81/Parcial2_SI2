import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SeccionesCrudComponent } from './secciones-crud.component';

@Component({
  selector: 'app-secciones',
  standalone: true,
  imports: [CommonModule, SeccionesCrudComponent],
  template: `<app-secciones-crud></app-secciones-crud>`
})
export class SeccionesComponent {}
