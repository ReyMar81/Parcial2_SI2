import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatChipsModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './perfil.component.html',
  styleUrls: ['./perfil.component.css']
})
export class PerfilComponent implements OnInit {
  perfil: any = null;

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.perfil = this.authService.perfil;
    this.authService.getPerfil().subscribe({
      next: (data: any) => {
        this.perfil = data;
      },
      error: (error: any) => {
        this.perfil = null;
      }
    });
  }

  get esSuperadmin(): boolean {
    return !!this.perfil?.is_superuser;
  }

  get esAlumno(): boolean {
    return !!this.perfil?.alumno;
  }

  get esTutor(): boolean {
    return !!this.perfil?.tutor;
  }

  get esMaestro(): boolean {
    return !!this.perfil?.maestro;
  }
}
