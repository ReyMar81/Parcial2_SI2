from django.db import models
from apps.personas.models import Maestro
from apps.secciones.models import SeccionGrado

class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)  # Nuevo campo para desactivación lógica

    def __str__(self):
        return self.nombre

class MateriaAsignada(models.Model):
    ciclo = models.CharField(max_length=50)
    horas_semanales = models.PositiveIntegerField()
    maestro = models.ForeignKey(Maestro, on_delete=models.CASCADE, related_name='materias_asignadas')
    seccion_grado = models.ForeignKey('secciones.SeccionGrado', on_delete=models.CASCADE, related_name='materias_asignadas')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='asignaciones')

    def __str__(self):
        return f"{self.materia} - {self.seccion_grado} ({self.ciclo})"

class TipoNota(models.Model):
    materia_asignada = models.ForeignKey('materias.MateriaAsignada', on_delete=models.CASCADE, related_name='tipos_nota')
    nombre = models.CharField(max_length=100)
    peso = models.FloatField()
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('materia_asignada', 'nombre')

    def __str__(self):
        return f"{self.nombre} ({self.peso}%)"

class ResultadoFinalMateria(models.Model):
    alumno = models.ForeignKey('personas.Alumno', on_delete=models.CASCADE)
    materia_asignada = models.ForeignKey('materias.MateriaAsignada', on_delete=models.CASCADE)
    ciclo = models.CharField(max_length=5)
    promedio = models.FloatField()
    aprobado = models.BooleanField()
    fecha_cierre = models.DateField()
    observacion = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('alumno', 'materia_asignada', 'ciclo')
