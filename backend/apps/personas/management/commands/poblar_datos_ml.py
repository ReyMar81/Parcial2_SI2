from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from apps.personas.services import crear_usuario_persona_rol
from apps.personas.models import Tutor, Alumno, TutorAlumno
from apps.secciones.models import Grado, Seccion, SeccionGrado, SeccionAlumno
from apps.materias.models import Materia, MateriaAsignada, TipoNota, ResultadoFinalMateria
from apps.evaluacion.models import Nota, Asistencia, Participacion
from apps.personas.models import Maestro

class Command(BaseCommand):
    help = 'Genera datos de prueba coherentes para ML (alumnos, tutores, maestros, inscripciones, notas, asistencias, participaciones)'

    def handle(self, *args, **options):
        fake = Faker()
        ciclos = ['2022', '2023', '2024']
        n_alumnos = 4000
        n_tutores = n_alumnos // 2
        n_maestros = 40
        n_materias = 20
        n_secciones = 10
        tipos_nota = [
            {'nombre': 'Examen', 'peso': 40},
            {'nombre': 'Tarea', 'peso': 30},
            {'nombre': 'Participación', 'peso': 30},
        ]
        # 1. Crear grados y secciones
        grados = [Grado.objects.get_or_create(nombre=f'Grado {i}', nivel='Primaria')[0] for i in range(1, 6)]
        secciones = [Seccion.objects.get_or_create(nombre=chr(65+i))[0] for i in range(n_secciones)]
        seccion_grados = []
        for grado in grados:
            for seccion in secciones:
                sg, _ = SeccionGrado.objects.get_or_create(grado=grado, seccion=seccion, aula=f'Aula {grado.nombre}-{seccion.nombre}', capacidad_maxima=60)
                seccion_grados.append(sg)
        # 2. Crear materias
        materias = [Materia.objects.get_or_create(nombre=f'Materia {i}', descripcion=fake.text())[0] for i in range(1, n_materias+1)]
        # 3. Crear maestros
        maestros = []
        for i in range(n_maestros):
            persona_data = {
                'nombre': fake.first_name(),
                'apellido_paterno': fake.last_name(),
                'apellido_materno': fake.last_name(),
                'genero': random.choice(['M', 'F']),
                'ci': f'MAESTRO{i+1:04d}',
                'direccion': fake.address(),
                'contacto': fake.phone_number(),
                'fecha_nacimiento': fake.date_of_birth(minimum_age=25, maximum_age=60)
            }
            maestro = crear_usuario_persona_rol(persona_data, rol='maestro', especialidad=fake.job())
            maestros.append(maestro)
        # 4. Asignar materias a maestros y secciones por ciclo
        materias_asignadas = []
        for ciclo in ciclos:
            for materia in materias:
                maestro = random.choice(maestros)
                seccion_grado = random.choice(seccion_grados)
                ma, _ = MateriaAsignada.objects.get_or_create(
                    ciclo=ciclo,
                    materia=materia,
                    maestro=maestro,
                    seccion_grado=seccion_grado,
                    horas_semanales=random.randint(2, 6)
                )
                materias_asignadas.append(ma)
                # Tipos de nota
                for tipo in tipos_nota:
                    TipoNota.objects.get_or_create(materia_asignada=ma, nombre=tipo['nombre'], defaults={'peso': tipo['peso']})
        # 5. Crear tutores
        tutores = []
        for i in range(n_tutores):
            persona_data = {
                'nombre': fake.first_name(),
                'apellido_paterno': fake.last_name(),
                'apellido_materno': fake.last_name(),
                'genero': random.choice(['M', 'F']),
                'ci': f'TUTOR{i+1:04d}',
                'direccion': fake.address(),
                'contacto': fake.phone_number(),
                'fecha_nacimiento': fake.date_of_birth(minimum_age=30, maximum_age=60)
            }
            tutor = crear_usuario_persona_rol(persona_data, rol='tutor', ocupacion=fake.job())
            tutores.append(tutor)
        # 6. Crear alumnos y asociar tutores
        alumnos = []
        for i in range(n_alumnos):
            persona_data = {
                'nombre': fake.first_name(),
                'apellido_paterno': fake.last_name(),
                'apellido_materno': fake.last_name(),
                'genero': random.choice(['M', 'F']),
                'ci': f'ALUMNO{i+1:05d}',
                'direccion': fake.address(),
                'contacto': fake.phone_number(),
                'fecha_nacimiento': fake.date_of_birth(minimum_age=6, maximum_age=18)
            }
            alumno = crear_usuario_persona_rol(persona_data, rol='alumno')
            alumnos.append(alumno)
            # Asociar 1 o 2 tutores
            for tutor in random.sample(tutores, k=random.choice([1,2])):
                TutorAlumno.objects.get_or_create(tutor=tutor, alumno=alumno, defaults={'tipo_relacion': 'Padre/Madre', 'activo': True})
        # 7. Inscribir alumnos en secciones por ciclo
        for ciclo in ciclos:
            for alumno in alumnos:
                seccion_grado = random.choice(seccion_grados)
                SeccionAlumno.objects.get_or_create(
                    alumno=alumno,
                    seccion_grado=seccion_grado,
                    ciclo=ciclo,
                    defaults={'fecha_inscripcion': timezone.now().date(), 'estado': 'activo'}
                )
        # 8. Registrar notas, asistencias y participaciones
        for ma in materias_asignadas:
            tipos = list(TipoNota.objects.filter(materia_asignada=ma))
            ciclo = ma.ciclo
            seccion_grado = ma.seccion_grado
            inscripciones = SeccionAlumno.objects.filter(seccion_grado=seccion_grado, ciclo=ciclo, estado='activo')
            for insc in inscripciones:
                alumno = insc.alumno
                for tipo in tipos:
                    calificacion = random.gauss(70, 15)
                    calificacion = max(0, min(100, calificacion))
                    Nota.objects.get_or_create(
                        alumno=alumno,
                        tipo_nota=tipo,
                        materia_asignada=ma,
                        defaults={'calificacion': calificacion, 'fecha': timezone.now().date()}
                    )
                # Asistencias (20 fechas por ciclo)
                for d in range(1, 21):
                    estado = random.choices(['presente', 'ausente', 'justificado'], weights=[0.85, 0.1, 0.05])[0]
                    Asistencia.objects.get_or_create(
                        alumno=alumno,
                        materia_asignada=ma,
                        fecha=timezone.now().date().replace(month=random.randint(1,12), day=random.randint(1,28)),
                        defaults={'estado': estado}
                    )
                # Participaciones (10 por ciclo)
                for d in range(10):
                    puntaje = max(0, min(10, random.gauss(7, 2)))
                    Participacion.objects.get_or_create(
                        alumno=alumno,
                        materia_asignada=ma,
                        fecha=timezone.now().date().replace(month=random.randint(1,12), day=random.randint(1,28)),
                        defaults={'puntaje': puntaje, 'observacion': fake.sentence()}
                    )
        self.stdout.write(self.style.SUCCESS('¡Datos de prueba generados exitosamente!'))
