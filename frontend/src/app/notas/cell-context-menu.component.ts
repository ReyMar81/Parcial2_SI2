import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { NgIf } from '@angular/common';

export interface CellContextMenuData {
  row: number;
  column: string;
  columnIndex: number;
  value?: number;
  cellRef: string; // Excel style cell reference (e.g., B2)
}

@Component({
  selector: 'app-cell-context-menu',
  template: `
    <div class="p-1 min-w-[180px]">
      <div class="flex items-center justify-between py-1 px-2 text-gray-500 text-sm border-b border-gray-200 mb-1">
        <span>{{ data.cellRef }}</span>
        <span *ngIf="data.value !== undefined">{{ data.value }}</span>
      </div>
      
      <button mat-menu-item class="w-full text-left flex items-center gap-3 py-1 px-2" (click)="onAction('copy')">
        <mat-icon class="text-gray-600">content_copy</mat-icon>
        <span>Copiar</span>
      </button>
      
      <button mat-menu-item class="w-full text-left flex items-center gap-3 py-1 px-2" (click)="onAction('paste')"
              [disabled]="!clipboard">
        <mat-icon class="text-gray-600">content_paste</mat-icon>
        <span>Pegar</span>
      </button>

      <mat-divider></mat-divider>

      <button mat-menu-item class="w-full text-left flex items-center gap-3 py-1 px-2" (click)="onAction('clear')">
        <mat-icon class="text-gray-600">clear</mat-icon>
        <span>Borrar contenido</span>
      </button>
    </div>
  `,
  standalone: true,
  imports: [
    NgIf,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    MatDividerModule
  ],
})
export class CellContextMenuComponent {
  // A simple clipboard for the component
  static clipboard: number | null = null;
  
  get clipboard(): number | null {
    return CellContextMenuComponent.clipboard;
  }

  constructor(
    public dialogRef: MatDialogRef<CellContextMenuComponent>,
    @Inject(MAT_DIALOG_DATA) public data: CellContextMenuData
  ) {}

  onAction(action: string): void {
    switch (action) {
      case 'copy':
        if (this.data.value !== undefined) {
          CellContextMenuComponent.clipboard = this.data.value;
        }
        break;
      case 'paste':
        if (CellContextMenuComponent.clipboard !== null) {
          this.dialogRef.close({ action, value: CellContextMenuComponent.clipboard });
          return;
        }
        break;
      case 'clear':
        this.dialogRef.close({ action, value: null });
        return;
    }
    this.dialogRef.close();
  }
}
