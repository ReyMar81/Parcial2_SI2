import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AsignacionesCrudComponent } from './asignaciones-crud.component';

@Component({
  selector: 'app-asignaciones',
  standalone: true,
  imports: [CommonModule, AsignacionesCrudComponent],
  template: `<app-asignaciones-crud></app-asignaciones-crud>`
})
export class AsignacionesComponent {}
