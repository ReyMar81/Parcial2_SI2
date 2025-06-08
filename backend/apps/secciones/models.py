from django.db import models
from apps.personas.models import Alumno

class Grado(models.Model):
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)  # Nuevo campo para desactivación lógica

    def __str__(self):
        return self.nombre

class Seccion(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class SeccionGrado(models.Model):
    aula = models.CharField(max_length=100)
    capacidad_maxima = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='seccion_grados')
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name='seccion_grados')

    def __str__(self):
        return f"{self.grado} {self.seccion} - {self.aula}"

    class Meta:
        unique_together = ('seccion', 'grado', 'aula')

class SeccionAlumno(models.Model):
    fecha_inscripcion = models.DateField()
    ciclo = models.CharField(max_length=5)
    estado = models.CharField(max_length=20, choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo')
    seccion_grado = models.ForeignKey(SeccionGrado, on_delete=models.CASCADE, related_name='inscripciones')
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='inscripciones')

    class Meta:
        unique_together = ('seccion_grado', 'alumno', 'ciclo')

    def __str__(self):
        return f"{self.alumno} en {self.seccion_grado}"

class ResultadoFinalSeccion(models.Model):
    ciclo = models.CharField(max_length=5)
    aprobado = models.BooleanField()
    fecha_cierre = models.DateField()
    seccion_alumno = models.ForeignKey(SeccionAlumno, on_delete=models.CASCADE, related_name='resultados_finales')

    def __str__(self):
        return f"{self.seccion_alumno} - {self.ciclo}"