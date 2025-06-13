import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard-welcome',
  standalone: true,
  templateUrl: './dashboard-welcome.component.html',
  styleUrls: ['./dashboard-welcome.component.css']
})
export class DashboardWelcomeComponent {
  materias = [
    { nombre: 'Lenguaje', ap: 100, er: 0 },
    { nombre: 'Matemática', ap: 80, er: 20 },
    { nombre: 'Física', ap: 60, er: 40 },
    { nombre: 'Química', ap: 50, er: 50 },
    { nombre: 'Inglés', ap: 90, er: 10 }
  ];

  // Devuelve el path SVG para un sector de pastel dado un porcentaje (0-100) y un offset inicial
  getPiePath(percent: number, offset: number = 0): string {
    const r = 16;
    const cx = 16;
    const cy = 16;
    const angle = (percent / 100) * 360;
    const startAngle = (offset / 100) * 360 - 90;
    const endAngle = startAngle + angle;
    const start = this.polarToCartesian(cx, cy, r, endAngle);
    const end = this.polarToCartesian(cx, cy, r, startAngle);
    const largeArcFlag = angle > 180 ? 1 : 0;
    return [
      `M ${cx} ${cy}`,
      `L ${start.x} ${start.y}`,
      `A ${r} ${r} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`,
      'Z'
    ].join(' ');
  }

  // Utilidad para convertir ángulo polar a coordenadas cartesianas
  polarToCartesian(cx: number, cy: number, r: number, angle: number) {
    const rad = (angle - 90) * Math.PI / 180.0;
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad)
    };
  }
}
