import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    FormsModule,
    HttpClientModule
  ],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class LoginComponent {
  username = '';
  password = '';
  constructor(private auth: AuthService) {}

  login() {
    this.auth.login(this.username, this.password).subscribe({
      next: (resp: any) => {
        this.auth.router.navigate(['/home']);
      },
      error: (err: any) => {
        alert('Usuario o contraseña incorrectos');
      }
    });
  }
}
