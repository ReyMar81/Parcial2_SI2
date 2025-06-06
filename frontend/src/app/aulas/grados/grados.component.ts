import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GradosCrudComponent } from './grados-crud.component';

@Component({
  selector: 'app-grados',
  standalone: true,
  imports: [CommonModule, GradosCrudComponent],
  template: `<app-grados-crud></app-grados-crud>`
})
export class GradosComponent {}
