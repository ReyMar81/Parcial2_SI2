from django.db import models
from apps.personas.models import Alumno
from apps.materias.models import MateriaAsignada, TipoNota

class Nota(models.Model):
    calificacion = models.FloatField()
    fecha = models.DateField()
    tipo_nota = models.ForeignKey(TipoNota, on_delete=models.CASCADE, related_name='notas')
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='notas')
    materia_asignada = models.ForeignKey(MateriaAsignada, on_delete=models.CASCADE, related_name='notas')

    class Meta:
        unique_together = ('alumno', 'tipo_nota')

class Asistencia(models.Model):
    fecha = models.DateField()
    estado = models.CharField(max_length=20)  # presente, ausente, etc.
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='asistencias')
    materia_asignada = models.ForeignKey(MateriaAsignada, on_delete=models.CASCADE, related_name='asistencias')

    def __str__(self):
        return f"{self.fecha} - {self.alumno} - {self.estado}"

class Participacion(models.Model):
    fecha = models.DateField()
    puntaje = models.FloatField()
    observacion = models.TextField(blank=True, null=True)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='participaciones')
    materia_asignada = models.ForeignKey(MateriaAsignada, on_delete=models.CASCADE, related_name='participaciones')

    def __str__(self):
        return f"{self.fecha} - {self.alumno} - {self.puntaje}"
