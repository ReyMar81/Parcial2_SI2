# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
import datetime
import calendar
from apps.personas.services import crear_usuario_persona_rol
from apps.personas.models import Tutor, Alumno, TutorAlumno, Persona, Maestro
from apps.secciones.models import Grado, Seccion, SeccionGrado, SeccionAlumno
from apps.materias.models import Materia, MateriaAsignada, TipoNota
from apps.evaluacion.models import Nota, Asistencia, Participacion
from django.db import transaction

CICLOS = ['2022', '2023', '2024', '2025']
GRADOS_SEC = [
    '1ro de Secundaria',
    '2do de Secundaria',
    '3ro de Secundaria',
    '4to de Secundaria'
]
SECCION_LETRAS = ['A', 'B']
MATERIAS = [
    ('Lenguaje', 'Lengua y literatura.'),
    ('Matemática', 'Matemáticas básicas y avanzadas.'),
    ('Física', 'Física general.'),
    ('Química', 'Química general.'),
    ('Inglés', 'Idioma extranjero inglés.')
]
MAESTROS = [
    {'especialidad': 'Lenguaje'},
    {'especialidad': 'Matemática'},
    {'especialidad': 'Física'},
    {'especialidad': 'Química'},
    {'especialidad': 'Inglés'}
]
TIPOS_NOTA = [
    {'nombre': 'Tarea 1', 'peso': 5},
    {'nombre': 'Tarea 2', 'peso': 5},
    {'nombre': 'Tarea 3', 'peso': 5},
    {'nombre': 'Tarea 4', 'peso': 5},
    {'nombre': 'Examen 1', 'peso': 15},
    {'nombre': 'Tarea 5', 'peso': 5},
    {'nombre': 'Exposición', 'peso': 10},
    {'nombre': 'Examen 2', 'peso': 15},
    {'nombre': 'Tarea 6', 'peso': 5},
    {'nombre': 'Tarea 7', 'peso': 5},
    {'nombre': 'Examen Final', 'peso': 25},
]

def dias_habiles_del_ano(year, meses=(3, 12)):
    dias = []
    for mes in range(meses[0], meses[1]):
        for dia in range(1, calendar.monthrange(year, mes)[1] + 1):
            fecha = datetime.date(year, mes, dia)
            if fecha.weekday() < 5:  # Lunes a viernes
                dias.append(fecha)
    return dias

class Command(BaseCommand):
    help = 'Pobla la base de datos académica para ML (2022-2025, 4 grados, 2 secciones, 5 materias, 5 maestros, 35 alumnos)'

    def handle(self, *args, **options):
        fake = Faker('es_ES')
        # 1. Crear grados y secciones
        grados = [Grado.objects.get_or_create(nombre=gn, nivel='Secundaria')[0] for gn in GRADOS_SEC]
        secciones = [Seccion.objects.get_or_create(nombre=letra)[0] for letra in SECCION_LETRAS]
        secciongrados = {}
        for grado in grados:
            for seccion in secciones:
                sg, _ = SeccionGrado.objects.get_or_create(grado=grado, seccion=seccion, aula=f'Aula {grado.nombre}-{seccion.nombre}', capacidad_maxima=40)
                secciongrados[(grado.nombre, seccion.nombre)] = sg
        # 2. Crear materias y maestros
        materias = [Materia.objects.get_or_create(nombre=nombre, descripcion=desc)[0] for nombre, desc in MATERIAS]
        maestros = []
        for i, maestro_info in enumerate(MAESTROS):
            genero = random.choice(['M', 'F'])
            nombre = fake.first_name_male() if genero == 'M' else fake.first_name_female()
            persona_data = {
                'nombre': nombre,
                'apellido_paterno': fake.last_name(),
                'apellido_materno': fake.last_name(),
                'genero': genero,
                'ci': f'MAESTRO{i+1:04d}',
                'direccion': fake.address(),
                'contacto': f'+591 {random.randint(60000000,79999999)}',
                'fecha_nacimiento': fake.date_of_birth(minimum_age=25, maximum_age=60),
            }
            maestro = crear_usuario_persona_rol(persona_data, rol='maestro', especialidad=maestro_info['especialidad'])
            maestros.append(maestro)
            print(f"Maestro: {nombre} {persona_data['apellido_paterno']} {persona_data['apellido_materno']} | Usuario: {maestro.persona.usuario.username} | Contraseña: {maestro.persona.ci}")
        # 3. Asignar materias a maestros por ciclo y sección_grado
        materia_asignada_map = {}
        for ciclo in CICLOS:
            for idx, materia in enumerate(materias):
                maestro = maestros[idx]
                for sg in secciongrados.values():
                    ma, _ = MateriaAsignada.objects.get_or_create(
                        ciclo=ciclo,
                        materia=materia,
                        maestro=maestro,
                        seccion_grado=sg,
                        horas_semanales=2
                    )
                    materia_asignada_map[(ciclo, materia.nombre, sg.id)] = ma
                    for tipo in TIPOS_NOTA:
                        TipoNota.objects.get_or_create(materia_asignada=ma, nombre=tipo['nombre'], defaults={'peso': tipo['peso']})
        # 4. Poblar históricos (2022-2024): solo sintéticos, variedad total
        from django.contrib.auth import get_user_model
        User = get_user_model()
        for ciclo in CICLOS:
            if ciclo == '2025':
                continue
            for grado in grados:
                for seccion in secciones:
                    sg = secciongrados[(grado.nombre, seccion.nombre)]
                    alumnos_sint = []
                    for i in range(35):
                        genero = random.choice(['M', 'F'])
                        nombre = fake.first_name_male() if genero == 'M' else fake.first_name_female()
                        username = f'sint_{ciclo}_{grado.nombre[0]}{seccion.nombre}_{i+1:05d}'
                        ci = f'SINT{ciclo}{grado.nombre[0]}{seccion.nombre}{i+1:05d}'
                        registro = f'SINT-{ciclo}-{grado.nombre[0]}{seccion.nombre}-{i+1:05d}'
                        # Crear usuario dummy único
                        user = User.objects.create_user(
                            username=username,
                            password=ci,
                            email=f'{username}@dummy.com'
                        )
                        persona_data = {
                            'nombre': nombre,
                            'apellido_paterno': fake.last_name(),
                            'apellido_materno': fake.last_name(),
                            'genero': genero,
                            'ci': ci,
                            'direccion': fake.address(),
                            'contacto': f'+591 {random.randint(60000000,79999999)}',
                            'fecha_nacimiento': fake.date_of_birth(minimum_age=11, maximum_age=18),
                            'usuario': user
                        }
                        persona = Persona.objects.create(**persona_data)
                        alumno = Alumno.objects.create(persona=persona, registro=registro)
                        SeccionAlumno.objects.get_or_create(
                            alumno=alumno,
                            seccion_grado=sg,
                            ciclo=ciclo,
                            defaults={'fecha_inscripcion': datetime.date(int(ciclo), 2, 10), 'estado': 'activo'}
                        )
                        alumnos_sint.append(alumno)
                    # Generar variedad de trayectorias
                    for idx, alumno in enumerate(alumnos_sint):
                        for materia in materias:
                            ma = materia_asignada_map[(ciclo, materia.nombre, sg.id)]
                            tipos = list(TipoNota.objects.filter(materia_asignada=ma))
                            # Diversidad: alternar trayectorias
                            if idx % 4 == 0:
                                # Malo con buena asistencia y participacion
                                notas = [round(random.uniform(20, 50), 2) for _ in tipos]
                                asistencia_pct = 0.95
                                participacion_pct = 0.7
                            elif idx % 4 == 1:
                                # Bueno con mala asistencia, buena participacion
                                notas = [round(random.uniform(80, 100), 2) for _ in tipos]
                                asistencia_pct = 0.5
                                participacion_pct = 0.7
                            elif idx % 4 == 2:
                                # Malo con excelente participacion y buena asistencia
                                notas = [round(random.uniform(20, 50), 2) for _ in tipos]
                                asistencia_pct = 0.85
                                participacion_pct = 0.95
                            else:
                                # Bueno con mala participacion
                                notas = [round(random.uniform(80, 100), 2) for _ in tipos]
                                asistencia_pct = 0.9
                                participacion_pct = 0.1
                            dias_habiles = dias_habiles_del_ano(int(ciclo), (3, 12))
                            for tipo, calificacion in zip(tipos, notas):
                                Nota.objects.create(
                                    alumno=alumno,
                                    tipo_nota=tipo,
                                    materia_asignada=ma,
                                    calificacion=calificacion,
                                    fecha=random.choice(dias_habiles)
                                )
                            # Asistencias
                            total_asist = int(len(dias_habiles) * asistencia_pct)
                            asistencias_bulk = []
                            for fecha in random.sample(dias_habiles, total_asist):
                                asistencias_bulk.append(Asistencia(
                                    alumno=alumno,
                                    materia_asignada=ma,
                                    fecha=fecha,
                                    estado='presente'
                                ))
                            Asistencia.objects.bulk_create(asistencias_bulk)
                            # Participaciones
                            total_part = int(len(dias_habiles) * participacion_pct)
                            participaciones_bulk = []
                            for fecha in random.sample(dias_habiles, total_part):
                                puntaje = round(random.uniform(5, 10), 2)
                                observacion = fake.sentence()
                                participaciones_bulk.append(Participacion(
                                    alumno=alumno,
                                    materia_asignada=ma,
                                    fecha=fecha,
                                    puntaje=puntaje,
                                    observacion=observacion
                                ))
                            Participacion.objects.bulk_create(participaciones_bulk)
        # 5. Ciclo 2025: alumnos reales con usuario y tutor, variedad total
        for grado in grados:
            for seccion in secciones:
                sg = secciongrados[(grado.nombre, seccion.nombre)]
                alumnos_2025 = []
                for i in range(35):
                    genero = random.choice(['M', 'F'])
                    nombre = fake.first_name_male() if genero == 'M' else fake.first_name_female()
                    persona_data = {
                        'nombre': nombre,
                        'apellido_paterno': fake.last_name(),
                        'apellido_materno': fake.last_name(),
                        'genero': genero,
                        'ci': f'ALUMNO2025{grado.nombre[0]}{seccion.nombre}{i+1:05d}',
                        'direccion': fake.address(),
                        'contacto': f'+591 {random.randint(60000000,79999999)}',
                        'fecha_nacimiento': fake.date_of_birth(minimum_age=11, maximum_age=18)
                    }
                    alumno = crear_usuario_persona_rol(persona_data, rol='alumno', ciclo_anio=2025)
                    # Tutor real
                    genero_t = random.choice(['M', 'F'])
                    nombre_t = fake.first_name_male() if genero_t == 'M' else fake.first_name_female()
                    tutor_data = {
                        'nombre': nombre_t,
                        'apellido_paterno': persona_data['apellido_paterno'],
                        'apellido_materno': persona_data['apellido_materno'],
                        'genero': genero_t,
                        'ci': f'TUTOR2025{grado.nombre[0]}{seccion.nombre}{i+1:05d}',
                        'direccion': fake.address(),
                        'contacto': f'+591 {random.randint(60000000,79999999)}',
                        'fecha_nacimiento': fake.date_of_birth(minimum_age=30, maximum_age=60),
                        'ocupacion': fake.job()
                    }
                    tutor = crear_usuario_persona_rol(tutor_data, rol='tutor', ocupacion=tutor_data['ocupacion'])
                    TutorAlumno.objects.get_or_create(tutor=tutor, alumno=alumno, defaults={'tipo_relacion': 'Padre/Madre', 'activo': True})
                    SeccionAlumno.objects.get_or_create(
                        alumno=alumno,
                        seccion_grado=sg,
                        ciclo='2025',
                        defaults={'fecha_inscripcion': datetime.date(2025, 2, 10), 'estado': 'activo'}
                    )
                    alumnos_2025.append(alumno)
                    print(f"Alumno: {nombre} {persona_data['apellido_paterno']} {persona_data['apellido_materno']} | Usuario: {alumno.persona.usuario.username} | Contraseña: {alumno.persona.ci}")
                    print(f"Tutor: {nombre_t} {persona_data['apellido_paterno']} {persona_data['apellido_materno']} | Usuario: {tutor.persona.usuario.username} | Contraseña: {tutor.persona.ci}")
                # Generar variedad de trayectorias en 2025
                for idx, alumno in enumerate(alumnos_2025):
                    for materia in materias:
                        ma = materia_asignada_map[("2025", materia.nombre, sg.id)]
                        tipos = list(TipoNota.objects.filter(materia_asignada=ma, nombre__startswith='Tarea').order_by('nombre'))[:4]
                        # Diversidad: alternar trayectorias
                        if idx % 4 == 0:
                            # Malo con buena asistencia y participacion
                            notas = [round(random.uniform(20, 50), 2) for _ in tipos]
                            asistencia_pct = 0.95
                            participacion_pct = 0.7
                        elif idx % 4 == 1:
                            # Bueno con mala asistencia, buena participacion
                            notas = [round(random.uniform(80, 100), 2) for _ in tipos]
                            asistencia_pct = 0.5
                            participacion_pct = 0.7
                        elif idx % 4 == 2:
                            # Malo con excelente participacion y buena asistencia
                            notas = [round(random.uniform(20, 50), 2) for _ in tipos]
                            asistencia_pct = 0.85
                            participacion_pct = 0.95
                        else:
                            # Bueno con mala participacion
                            notas = [round(random.uniform(80, 100), 2) for _ in tipos]
                            asistencia_pct = 0.9
                            participacion_pct = 0.1
                        dias_habiles = [d for d in dias_habiles_del_ano(2025, (3, 6)) if d <= datetime.date.today()]
                        for tipo, calificacion in zip(tipos, notas):
                            Nota.objects.create(
                                alumno=alumno,
                                tipo_nota=tipo,
                                materia_asignada=ma,
                                calificacion=calificacion,
                                fecha=random.choice(dias_habiles)
                            )
                        # Asistencias
                        total_asist = int(len(dias_habiles) * asistencia_pct)
                        asistencias_bulk = []
                        for fecha in random.sample(dias_habiles, total_asist):
                            asistencias_bulk.append(Asistencia(
                                alumno=alumno,
                                materia_asignada=ma,
                                fecha=fecha,
                                estado='presente'
                            ))
                        Asistencia.objects.bulk_create(asistencias_bulk)
                        # Participaciones
                        total_part = int(len(dias_habiles) * participacion_pct)
                        participaciones_bulk = []
                        for fecha in random.sample(dias_habiles, total_part):
                            puntaje = round(random.uniform(5, 10), 2)
                            observacion = fake.sentence()
                            participaciones_bulk.append(Participacion(
                                alumno=alumno,
                                materia_asignada=ma,
                                fecha=fecha,
                                puntaje=puntaje,
                                observacion=observacion
                            ))
                        Participacion.objects.bulk_create(participaciones_bulk)
        print("¡Base de datos poblada exitosamente para ML!")