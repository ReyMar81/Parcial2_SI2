import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../auth.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-dashboard-welcome',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard-welcome.component.html',
  styleUrls: ['./dashboard-welcome.component.css']
})
export class DashboardWelcomeComponent {
  constructor(private auth: AuthService) {}
}
