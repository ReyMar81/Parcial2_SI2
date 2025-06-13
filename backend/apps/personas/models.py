from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Persona(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='persona')
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    genero = models.CharField(max_length=10)
    ci = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=200)
    contacto = models.CharField(max_length=50, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    activo = models.BooleanField(default=True)  # Nuevo campo

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"

class Alumno(models.Model):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name='alumno')
    registro = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)  # Nuevo campo

    def __str__(self):
        return str(self.persona)

class Maestro(models.Model):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name='maestro')
    especialidad = models.CharField(max_length=100)
    registro = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)  # Nuevo campo

    def __str__(self):
        return str(self.persona)

class Tutor(models.Model):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name='tutor')
    ocupacion = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)  # Nuevo campo

    def __str__(self):
        return str(self.persona)

class TutorAlumno(models.Model):
    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='alumnos_asociados')
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE, related_name='tutores_asociados')
    fecha_asignacion = models.DateField(auto_now_add=True)
    tipo_relacion = models.CharField(max_length=50, blank=True, null=True)
    activo = models.BooleanField(default=True)  # Nuevo campo para desactivación lógica

    class Meta:
        unique_together = ('tutor', 'alumno')

    def __str__(self):
        return f"{self.tutor} - {self.alumno} ({self.tipo_relacion})"

class FCMToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fcm_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.token[:10]}..."