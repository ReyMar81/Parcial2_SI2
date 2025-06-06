from django.db import models
from apps.personas.models import Alumno

class Grado(models.Model):
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Seccion(models.Model):
    nombre = models.CharField(max_length=100)
    aula = models.CharField(max_length=100)
    capacidad_maxima = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=[('activa', 'Activa'), ('cerrada', 'Cerrada')], default='activa')
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name='secciones')

    def __str__(self):
        return f"{self.nombre} - {self.aula}"

class SeccionAlumno(models.Model):
    fecha_inscripcion = models.DateField()
    ciclo = models.CharField(max_length=5)
    estado = models.CharField(max_length=20, choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo')
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='inscripciones')
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='inscripciones')

    class Meta:
        unique_together = ('seccion', 'alumno', 'ciclo')

    def __str__(self):
        return f"{self.alumno} en {self.seccion}"

class ResultadoFinalSeccion(models.Model):
    ciclo = models.CharField(max_length=5)
    aprobado = models.BooleanField()
    fecha_cierre = models.DateField()
    seccion_alumno = models.ForeignKey(SeccionAlumno, on_delete=models.CASCADE, related_name='resultados_finales')

    def __str__(self):
        return f"{self.seccion_alumno} - {self.ciclo}"