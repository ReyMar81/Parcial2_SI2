import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';

export interface TipoNotaDialogData {
  nombre: string;
  peso: number;
  nivel: number;
  color?: string;
  isEdit?: boolean;
}

@Component({
  selector: 'app-tipo-nota-dialog',
  templateUrl: './tipo-nota-dialog.component.html',
  styleUrls: ['./tipo-nota-dialog.component.css'],
  standalone: true,
  imports: [
    NgIf,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatDialogModule,
    MatIconModule,
  ],
})
export class TipoNotaDialogComponent {
  form: FormGroup;
  selectedColor: string = 'bg-blue-200'; // Default color

  constructor(
    public dialogRef: MatDialogRef<TipoNotaDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: TipoNotaDialogData,
    private fb: FormBuilder
  ) {
    // Initialize selected color from data if available
    if (data.color) {
      this.selectedColor = data.color;
    }
    
    this.form = this.fb.group({
      nombre: [data.nombre || '', [Validators.required, Validators.maxLength(30)]],
      peso: [data.peso ?? 0, [Validators.required, Validators.min(0), Validators.max(100)]],
      nivel: [data.nivel ?? 1, [Validators.required, Validators.min(1)]],
    });
  }
  
  selectColor(color: string): void {
    this.selectedColor = color;
  }

  onCancel(): void {
    this.dialogRef.close();
  }
  onSave(): void {
    if (this.form.valid) {
      const result = {
        ...this.form.value,
        color: this.selectedColor
      };
      this.dialogRef.close(result);
    }
  }
}
