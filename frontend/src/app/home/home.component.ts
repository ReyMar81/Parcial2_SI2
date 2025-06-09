import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatMenuModule,
    MatSlideToggleModule,
    MatDividerModule,
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  private router = inject(Router);
  username = '';
  avatarUrl = '';
  collapsed = false;
  darkMode = false;
  usuariosSubmenuOpen = false;
  materiasSubmenuOpen = false;
  aulasSubmenuOpen = false;
  notasSubmenuOpen = false;

  ngOnInit() {
    if (!localStorage.getItem('access_token')) {
      this.router.navigate(['/']);
    }
    this.username = this.getUsernameFromToken() || 'Usuario';
    this.avatarUrl = '';
    this.darkMode = localStorage.getItem('darkMode') === 'true';
    this.setDarkClass(this.darkMode);
    window.scrollTo(0, 0);
  }
  toggleSidebar() { this.collapsed = !this.collapsed; }
  navigate(ruta: string) {
    if (!ruta) { this.router.navigate(['/home']); }
    else { this.router.navigate(['/home', ruta]); }
  }
  logout() {
    localStorage.removeItem('access_token');
    this.router.navigate(['/']);
  }
  toggleDarkMode() {
    this.darkMode = !this.darkMode;
    localStorage.setItem('darkMode', this.darkMode ? 'true' : 'false');
    this.setDarkClass(this.darkMode);
  }
  setDarkClass(isDark: boolean) {
    const html = document.documentElement;
    if (isDark) { html.classList.add('dark'); }
    else { html.classList.remove('dark'); }
  }
  getUsernameFromToken(): string | null {
    const token = localStorage.getItem('access_token');
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.username || payload.user || null;
    } catch { return null; }
  }
  toggleSubmenu(menu: 'usuarios' | 'materias' | 'aulas' | 'notas') {
    this.usuariosSubmenuOpen = menu === 'usuarios' ? !this.usuariosSubmenuOpen : false;
    this.materiasSubmenuOpen = menu === 'materias' ? !this.materiasSubmenuOpen : false;
    this.aulasSubmenuOpen = menu === 'aulas' ? !this.aulasSubmenuOpen : false;
    this.notasSubmenuOpen = menu === 'notas' ? !this.notasSubmenuOpen : false;
  }
}
