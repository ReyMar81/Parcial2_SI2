# -*- coding: utf-8 -*-
"""
Script adaptado para poblar un colegio de secundaria en Bolivia.
- 6 grados (1ro a 6to de secundaria), solo nivel secundaria.
- Secciones A, B, C, D por grado, abiertas según demanda y capacidad máxima (ej: 40).
- Progresión realista: alumnos avanzan de grado/sección si aprueban, repiten si no, egresan al terminar 6to.
- Inscripción de nuevos solo en 1ro cada ciclo, llenando secciones según capacidad.
- Datos y descripciones en español, celulares bolivianos (+591).
- Materias típicas de secundaria boliviana.
- Mantiene lógica de notas, asistencias, participaciones, tutores, maestros, etc.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
import datetime
from collections import defaultdict
from apps.personas.services import crear_usuario_persona_rol
from apps.personas.models import Tutor, Alumno, TutorAlumno, Persona, Maestro
from apps.secciones.models import Grado, Seccion, SeccionGrado, SeccionAlumno
from apps.materias.models import Materia, MateriaAsignada, TipoNota, ResultadoFinalMateria
from apps.evaluacion.models import Nota, Asistencia, Participacion
from django.db import transaction, IntegrityError
from django.db.models import Max
import re
import os

# --- Configuración general ---
CICLOS = ['2022', '2023', '2024', '2025']
GRADOS_SEC = [
    f'{i}ro de Secundaria' if i in (1, 3) else
    (f'{i}do de Secundaria' if i == 2 else
     f'{i}to de Secundaria')
    for i in range(1, 7)
]
SECCION_LETRAS = ['A', 'B', 'C', 'D']
CAPACIDAD_MAXIMA = 40
N_MAESTROS = 40
N_TUTORES = 1000
N_ALUMNOS_NUEVOS_1RO = 160  # por ciclo, ajustable
MATERIAS_SECUNDARIA = [
    ('Matemáticas', 'Estudio de números, álgebra, geometría y estadística.'),
    ('Lengua y Literatura', 'Comprensión lectora, gramática y redacción.'),
    ('Ciencias Naturales', 'Biología, física y química básica.'),
    ('Ciencias Sociales', 'Historia, geografía y educación cívica.'),
    ('Educación Física', 'Actividad física y deportes.'),
    ('Inglés', 'Idioma extranjero.'),
    ('Filosofía', 'Pensamiento crítico y lógica.'),
    ('Física', 'Estudio de la materia y energía.'),
    ('Química', 'Estudio de sustancias y reacciones.'),
    ('Biología', 'Estudio de los seres vivos.'),
    ('Música', 'Educación musical y apreciación artística.'),
    ('Artes Plásticas', 'Dibujo, pintura y escultura.'),
]
TIPOS_NOTA = [
    {'nombre': 'Tarea 1', 'peso': 10},
    {'nombre': 'Tarea 2', 'peso': 10},
    {'nombre': 'Examen 1', 'peso': 15},
    {'nombre': 'Tarea 3', 'peso': 10},
    {'nombre': 'Tarea 4', 'peso': 10},
    {'nombre': 'Examen 2', 'peso': 15},
    {'nombre': 'Examen Final', 'peso': 30},
]

BATCH_SIZE = 5000

class Command(BaseCommand):
    help = 'Genera datos de prueba coherentes para ML (secundaria Bolivia, progresión realista, secciones dinámicas, datos en español)'

    def crear_alumno_con_registro(self, persona_data, ciclo_anio):
        persona = Persona.objects.filter(ci=persona_data['ci']).first()
        if persona:
            alumno_obj = Alumno.objects.get(persona=persona)
            return alumno_obj
        else:
            base_registro = f"{ciclo_anio}02"  # "202202"
            max_registro = Alumno.objects.filter(registro__startswith=base_registro).aggregate(Max('registro'))['registro__max']
            if max_registro:
                next_seq = int(max_registro[-4:]) + 1
            else:
                next_seq = 1
            registro = f"{ciclo_anio}02{str(next_seq).zfill(4)}"
            alumno_obj = crear_usuario_persona_rol(persona_data, rol='alumno', ciclo_anio=ciclo_anio, registro=registro)
            return alumno_obj

    def crear_maestro_con_registro(self, persona_data, ciclo_anio):
        persona = Persona.objects.filter(ci=persona_data['ci']).first()
        if persona:
            maestro_obj = Maestro.objects.get(persona=persona)
            return maestro_obj
        else:
            base_registro = f"{ciclo_anio}01"
            max_registro = Maestro.objects.filter(registro__startswith=base_registro).aggregate(Max('registro'))['registro__max']
            if max_registro:
                next_seq = int(max_registro[-4:]) + 1
            else:
                next_seq = 1
            registro = f"{ciclo_anio}01{str(next_seq).zfill(4)}"
            maestro_obj = crear_usuario_persona_rol(persona_data, rol='maestro', ciclo_anio=ciclo_anio)
            return maestro_obj

    def handle(self, *args, **options):
        fake = Faker('es_ES')
        # --- Inicialización de entidades base ---
        grados = [Grado.objects.get_or_create(nombre=gn, nivel='Secundaria')[0] for gn in GRADOS_SEC]
        secciones = [Seccion.objects.get_or_create(nombre=letra)[0] for letra in SECCION_LETRAS]
        materias = [Materia.objects.get_or_create(nombre=nombre, descripcion=desc)[0] for nombre, desc in MATERIAS_SECUNDARIA]
        credenciales_creadas = []

        # --- Crear maestros ---
        maestros = self.crear_maestros(fake, N_MAESTROS, credenciales_creadas)
        # --- Crear tutores ---
        tutores = self.crear_tutores(fake, N_TUTORES, credenciales_creadas)

        # --- Inicializar estructuras de control ---
        estado_alumnos_por_ciclo = defaultdict(dict)
        secciongrados_por_ciclo = defaultdict(lambda: defaultdict(dict))
        resumen_ciclos = {}
        alumnos_id, registro_id = self.obtener_max_ids()
        asignacion_maestros = {}
        historial_alumnos = []

        # --- Proceso principal por ciclo ---
        for ciclo in CICLOS:
            print(f'\n--- Ciclo {ciclo} ---')
            resumen_ciclos[ciclo] = {'inscritos': defaultdict(lambda: defaultdict(list)), 'egresados': [], 'repitentes': [], 'abandonos': []}
            # a) Progresión de alumnos existentes
            if ciclo != CICLOS[0]:
                self.progresar_alumnos(ciclo, CICLOS, GRADOS_SEC, estado_alumnos_por_ciclo, resumen_ciclos)
            # b) Inscribir nuevos en 1ro SOLO si hay cupo
            if ciclo == CICLOS[0]:
                alumnos_id = self.inscribir_nuevos_1ro(
                    fake, ciclo, N_ALUMNOS_NUEVOS_1RO, historial_alumnos, tutores, self.crear_alumno_con_registro,
                    estado_alumnos_por_ciclo, secciones, GRADOS_SEC, alumnos_id
                )
            # c) Marcar inscripciones previas como inactivas
            if ciclo != CICLOS[0]:
                self.marcar_inscripciones_previas_inactivas(ciclo, estado_alumnos_por_ciclo)
            # d) Crear SeccionGrado y SeccionAlumno (inscripciones)
            self.crear_inscripciones(
                ciclo, GRADOS_SEC, secciones, estado_alumnos_por_ciclo, secciongrados_por_ciclo,
                resumen_ciclos, capacidad_maxima=CAPACIDAD_MAXIMA
            )
            # e) Asignar materias a maestros y secciones por ciclo
            materias_asignadas = self.asignar_materias(
                ciclo, grados, secciones, MATERIAS_SECUNDARIA, materias, asignacion_maestros, maestros, TIPOS_NOTA, secciongrados_por_ciclo
            )
            # f) Simular cambios de tutor
            self.simular_cambios_tutor(ciclo, estado_alumnos_por_ciclo, tutores)
            # g) Poblar notas, asistencias, participaciones
            self.poblar_eventos_academicos(
                ciclo, materias_asignadas, TIPOS_NOTA, secciongrados_por_ciclo, estado_alumnos_por_ciclo,
                GRADOS_SEC, secciones, fake, BATCH_SIZE
            )

        # --- Exportar credenciales de usuarios activos en 2025 ---
        self.exportar_credenciales_2025()
        self.stdout.write(self.style.SUCCESS('¡Datos de prueba generados exitosamente!'))

    # --- Métodos auxiliares agrupados para claridad ---
    def crear_maestros(self, fake, n_maestros, credenciales_creadas):
        maestros = []
        especialidades = [m[0] for m in MATERIAS_SECUNDARIA]
        for i in range(n_maestros):
            genero = random.choice(['M', 'F'])
            nombre = fake.first_name_male() if genero == 'M' else fake.first_name_female()
            especialidad = random.choice(especialidades)
            persona_data = {
                'nombre': nombre,
                'apellido_paterno': fake.last_name(),
                'apellido_materno': fake.last_name(),
                'genero': genero,
                'ci': f'MAESTRO{i+1:04d}',
                'direccion': fake.address(),
                'contacto': f'+591 {random.randint(60000000,79999999)}',
                'fecha_nacimiento': fake.date_of_birth(minimum_age=25, maximum_age=60),
                'especialidad': especialidad
            }
            existe = Maestro.objects.filter(persona__ci=persona_data['ci']).exists()
            if not existe:
                maestro = self.crear_maestro_con_registro(persona_data, ciclo_anio=2022)
                # Asignar especialidad si el modelo Maestro la tiene
                if hasattr(maestro, 'especialidad'):
                    maestro.especialidad = especialidad
                    maestro.save()
                maestros.append(maestro)
                credenciales_creadas.append({
                    'rol': 'Maestro',
                    'username': maestro.persona.usuario.username,
                    'nombre': f"{persona_data['nombre']} {persona_data['apellido_paterno']} {persona_data['apellido_materno']}",
                    'password': persona_data['ci']
                })
            else:
                maestro = Maestro.objects.get(persona__ci=persona_data['ci'])
                maestros.append(maestro)
        return maestros

    def crear_tutores(self, fake, n_tutores, credenciales_creadas, alumnos=None):
        tutores = []
        alumnos_asignados = set()
        for i in range(n_tutores):
            genero = random.choice(['M', 'F'])
            nombre = fake.first_name_male() if genero == 'M' else fake.first_name_female()
            persona_data = {
                'nombre': nombre,
                'apellido_paterno': fake.last_name(),
                'apellido_materno': fake.last_name(),
                'genero': genero,
                'ci': f'TUTOR{i+1:04d}',
                'direccion': fake.address(),
                'contacto': f'+591 {random.randint(60000000,79999999)}',
                'fecha_nacimiento': fake.date_of_birth(minimum_age=30, maximum_age=60)
            }
            existe = Tutor.objects.filter(persona__ci=persona_data['ci']).exists()
            if not existe:
                tutor = crear_usuario_persona_rol(persona_data, rol='tutor', ocupacion=fake.job())
                tutores.append(tutor)
                credenciales_creadas.append({
                    'rol': 'Tutor',
                    'username': tutor.persona.usuario.username,
                    'nombre': f"{persona_data['nombre']} {persona_data['apellido_paterno']} {persona_data['apellido_materno']}",
                    'password': persona_data['ci']
                })
            else:
                tutor = Tutor.objects.get(persona__ci=persona_data['ci'])
                tutores.append(tutor)
        # Asignar al menos un alumno a cada tutor si hay alumnos
        if alumnos:
            for idx, tutor in enumerate(tutores):
                alumno = alumnos[idx % len(alumnos)]
                TutorAlumno.objects.get_or_create(tutor=tutor, alumno=alumno, defaults={'tipo_relacion': 'Padre/Madre', 'activo': True})
        return tutores

    def obtener_max_ids(self):
        max_id = 0
        max_registro = 0
        for persona in Persona.objects.filter(ci__startswith='ALUMNO'):
            match = re.match(r'ALUMNO(\d{5})', persona.ci)
            if match:
                num = int(match.group(1))
                if num > max_id:
                    max_id = num
        for alumno in Alumno.objects.all():
            match = re.match(r'(\d{4})(\d{5})', str(alumno.registro))
            if match:
                num = int(match.group(2))
                if num > max_registro:
                    max_registro = num
        return max_id + 1, max_registro + 1

    def progresar_alumnos(self, ciclo, ciclos, grados_sec, estado_alumnos_por_ciclo, resumen_ciclos):
        ciclo_ant = str(int(ciclo)-1)
        for alumno_id, info_ant in estado_alumnos_por_ciclo[ciclo_ant].items():
            if info_ant['estado'] in ['egreso', 'abandono']:
                continue
            if info_ant['estado'] == 'aprobado':
                if info_ant['grado'] == '6to de Secundaria':
                    estado_alumnos_por_ciclo[ciclo][alumno_id] = {**info_ant, 'estado': 'egreso'}
                    continue
                grado_idx = grados_sec.index(info_ant['grado'])
                nuevo_grado = grados_sec[grado_idx+1]
                estado_alumnos_por_ciclo[ciclo][alumno_id] = {
                    'estado': 'pendiente',
                    'grado': nuevo_grado,
                    'seccion': info_ant['seccion'],
                    'alumno_obj': info_ant['alumno_obj']
                }
            elif info_ant['estado'] == 'reprobado':
                estado_alumnos_por_ciclo[ciclo][alumno_id] = {
                    'estado': 'pendiente',
                    'grado': info_ant['grado'],
                    'seccion': info_ant['seccion'],
                    'alumno_obj': info_ant['alumno_obj']
                }
                resumen_ciclos[ciclo]['repitentes'].append(alumno_id)

    def inscribir_nuevos_1ro(self, fake, ciclo, n_alumnos_nuevos_1ro, historial_alumnos, tutores, crear_alumno_con_registro, estado_alumnos_por_ciclo, secciones, grados_sec, alumnos_id):
        nuevos_1ro = []
        n_hermanos = int(n_alumnos_nuevos_1ro * random.uniform(0.2, 0.3))
        n_normales = n_alumnos_nuevos_1ro - n_hermanos
        posibles_hermanos = [a for a in historial_alumnos if a['tutores']]
        for _ in range(n_hermanos):
            if not posibles_hermanos:
                break
            base = random.choice(posibles_hermanos)
            tutor = random.choice(base['tutores'])
            apellido_paterno = base['apellido_paterno']
            apellido_materno = base['apellido_materno']
            genero = random.choice(['M', 'F'])
            nombre = fake.first_name_male() if genero == 'M' else fake.first_name_female()
            edad_base = (datetime.date.today().year - base['fecha_nacimiento'].year)
            edad_hermano = max(11, min(18, edad_base - random.randint(1, 5)))
            fecha_nacimiento = fake.date_of_birth(minimum_age=edad_hermano, maximum_age=edad_hermano)
            persona_data = {
                'nombre': nombre,
                'apellido_paterno': apellido_paterno,
                'apellido_materno': apellido_materno,
                'genero': genero,
                'ci': f'ALUMNO{alumnos_id:05d}',
                'direccion': fake.address(),
                'contacto': f'+591 {random.randint(60000000,79999999)}',
                'fecha_nacimiento': fecha_nacimiento
            }
            alumno_obj = crear_alumno_con_registro(persona_data, ciclo_anio=int(ciclo))
            TutorAlumno.objects.get_or_create(tutor=tutor, alumno=alumno_obj, defaults={'tipo_relacion': 'Padre/Madre', 'activo': True})
            nuevos_1ro.append({'id': alumnos_id, 'alumno_obj': alumno_obj, 'apellido_paterno': apellido_paterno, 'apellido_materno': apellido_materno, 'tutores': [tutor], 'fecha_nacimiento': fecha_nacimiento})
            alumnos_id += 1
        for _ in range(n_normales):
            genero = random.choice(['M', 'F'])
            nombre = fake.first_name_male() if genero == 'M' else fake.first_name_female()
            persona_data = {
                'nombre': nombre,
                'apellido_paterno': fake.last_name(),
                'apellido_materno': fake.last_name(),
                'genero': genero,
                'ci': f'ALUMNO{alumnos_id:05d}',
                'direccion': fake.address(),
                'contacto': f'+591 {random.randint(60000000,79999999)}',
                'fecha_nacimiento': fake.date_of_birth(minimum_age=11, maximum_age=13)
            }
            alumno_obj = crear_alumno_con_registro(persona_data, ciclo_anio=int(ciclo))
            tutor = random.choice(tutores)
            TutorAlumno.objects.get_or_create(tutor=tutor, alumno=alumno_obj, defaults={'tipo_relacion': 'Padre/Madre', 'activo': True})
            nuevos_1ro.append({'id': alumnos_id, 'alumno_obj': alumno_obj, 'apellido_paterno': persona_data['apellido_paterno'], 'apellido_materno': persona_data['apellido_materno'], 'tutores': [tutor], 'fecha_nacimiento': persona_data['fecha_nacimiento']})
            alumnos_id += 1
        for alumno in nuevos_1ro:
            asignado = False
            for seccion in secciones:
                grado = grados_sec[0]
                inscritos = [a for a in estado_alumnos_por_ciclo[ciclo].values() if a['grado']==grado and a['seccion']==seccion.nombre]
                if len(inscritos) < CAPACIDAD_MAXIMA:
                    estado_alumnos_por_ciclo[ciclo][alumno['id']] = {
                        'estado': 'pendiente',
                        'grado': grado,
                        'seccion': seccion.nombre,
                        'alumno_obj': alumno['alumno_obj']
                    }
                    historial_alumnos.append(alumno)
                    asignado = True
                    break
            if not asignado:
                print(f"No hay cupo para alumno nuevo {alumno['id']} en 1ro de Secundaria")
        return alumnos_id

    def marcar_inscripciones_previas_inactivas(self, ciclo, estado_alumnos_por_ciclo):
        for alumno_id, info in estado_alumnos_por_ciclo[ciclo].items():
            insc_previas = SeccionAlumno.objects.filter(alumno=info['alumno_obj'], estado='activo').exclude(ciclo=ciclo)
            for insc in insc_previas:
                insc.estado = 'inactivo'
                insc.save()

    def crear_inscripciones(self, ciclo, grados_sec, secciones, estado_alumnos_por_ciclo, secciongrados_por_ciclo, resumen_ciclos, capacidad_maxima):
        for grado in grados_sec:
            for seccion in secciones:
                inscritos = [a for a in estado_alumnos_por_ciclo[ciclo].values() if a['grado']==grado and a['seccion']==seccion.nombre and a['estado'] not in ['egreso','abandono']]
                sg, _ = SeccionGrado.objects.get_or_create(grado=Grado.objects.get(nombre=grado), seccion=seccion, aula=f'Aula {grado}-{seccion.nombre}', capacidad_maxima=capacidad_maxima)
                secciongrados_por_ciclo[ciclo][grado][seccion.nombre] = sg
                if inscritos:
                    n = len(inscritos)
                    n_repitentes = max(1, int(n*0.02)) if n > 1 else 0
                    repitentes_ids = set(random.sample([a['alumno_obj'].id for a in inscritos], n_repitentes)) if n_repitentes else set()
                    for alumno in inscritos:
                        anio = int(ciclo)
                        fecha_ini = datetime.date(anio, 2, 1)
                        fecha_fin = datetime.date(anio, 3, 31)
                        fecha_insc = Faker('es_ES').date_between_dates(date_start=fecha_ini, date_end=fecha_fin)
                        SeccionAlumno.objects.get_or_create(
                            alumno=alumno['alumno_obj'],
                            seccion_grado=sg,
                            ciclo=ciclo,
                            defaults={'fecha_inscripcion': fecha_insc, 'estado': 'activo'}
                        )
                        resumen_ciclos[ciclo]['inscritos'][grado][seccion.nombre].append(alumno['alumno_obj'].id)
                        alumno['forzar_reprobado'] = alumno['alumno_obj'].id in repitentes_ids

    def asignar_materias(self, ciclo, grados, secciones, materias_secundaria, materias, asignacion_maestros, maestros, tipos_nota, secciongrados_por_ciclo):
        materias_asignadas = []
        maestro_idx = 0
        maestros_cantidad = len(maestros)
        for grado in grados:
            for seccion in secciones:
                sg = secciongrados_por_ciclo[ciclo].get(grado.nombre, {}).get(seccion.nombre)
                if not sg:
                    continue
                # Solo asignar materias si hay alumnos inscritos en la sección-grado
                alumnos_inscritos = sg.seccionalumno_set.filter(ciclo=ciclo, estado='activo').count()
                if alumnos_inscritos == 0:
                    continue
                for nombre, desc in materias_secundaria:
                    materia = [m for m in materias if m.nombre == nombre][0]
                    # Asignar maestros de forma equitativa y rotativa
                    maestro = maestros[maestro_idx % maestros_cantidad]
                    maestro_idx += 1
                    key = (materia.nombre, grado.nombre, seccion.nombre)
                    asignacion_maestros[key] = maestro
                    ma, _ = MateriaAsignada.objects.get_or_create(
                        ciclo=ciclo,
                        materia=materia,
                        maestro=maestro,
                        seccion_grado=sg,
                        horas_semanales=random.randint(2, 6)
                    )
                    materias_asignadas.append(ma)
                    for tipo in tipos_nota:
                        TipoNota.objects.get_or_create(materia_asignada=ma, nombre=tipo['nombre'], defaults={'peso': tipo['peso']})
        return materias_asignadas

    def simular_cambios_tutor(self, ciclo, estado_alumnos_por_ciclo, tutores):
        for alumno_id, info in estado_alumnos_por_ciclo[ciclo].items():
            if random.random() < 0.02:
                relaciones = TutorAlumno.objects.filter(alumno=info['alumno_obj'], activo=True)
                if relaciones.exists() and random.random() < 0.5:
                    rel = random.choice(list(relaciones))
                    rel.activo = False
                    rel.save()
                else:
                    nuevo_tutor = random.choice(tutores)
                    TutorAlumno.objects.get_or_create(tutor=nuevo_tutor, alumno=info['alumno_obj'], defaults={'tipo_relacion': 'Tío/Tía', 'activo': True})

    def poblar_eventos_academicos(self, ciclo, materias_asignadas, tipos_nota, secciongrados_por_ciclo, estado_alumnos_por_ciclo, grados_sec, secciones, fake, batch_size):
        notas_bulk = []
        asistencias_bulk = []
        participaciones_bulk = []
        notas_count = asistencias_count = participaciones_count = 0
        if ciclo == '2025':
            fecha_evento_ini = datetime.date(2025, 3, 1)
            fecha_evento_fin = datetime.date(2025, 5, 31)
        else:
            fecha_evento_ini = datetime.date(int(ciclo), 3, 1)
            fecha_evento_fin = datetime.date(int(ciclo), 11, 30)
        meses_validos = list(range(fecha_evento_ini.month, fecha_evento_fin.month+1))
        dias_validos = [0, 1, 2, 3, 4]
        print('Generando notas, asistencias y participaciones...')
        for ma in materias_asignadas:
            tipos = list(TipoNota.objects.filter(materia_asignada=ma))
            ciclo_ma = ma.ciclo
            seccion_grado = ma.seccion_grado
            inscripciones = SeccionAlumno.objects.filter(seccion_grado=seccion_grado, ciclo=ciclo_ma, estado='activo')
            alumnos_estado = {}
            for grado in grados_sec:
                for seccion in secciones:
                    sg_ref = secciongrados_por_ciclo[ciclo].get(grado, {}).get(seccion.nombre)
                    if sg_ref and sg_ref == seccion_grado:
                        for a in estado_alumnos_por_ciclo[ciclo].values():
                            if a['grado']==grado and a['seccion']==seccion.nombre and a['estado'] not in ['egreso','abandono']:
                                alumnos_estado[a['alumno_obj'].id] = a.get('forzar_reprobado', False)
            for insc in inscripciones:
                alumno = insc.alumno
                forzar_reprobado = alumnos_estado.get(alumno.id, False)
                notas_alumno = []
                for tipo in tipos:
                    if forzar_reprobado:
                        calificacion = round(max(0, min(50, random.gauss(40, 8))), 2)
                    else:
                        calificacion = round(max(51, min(100, random.gauss(70, 10))), 2)
                    notas_alumno.append((tipo, calificacion))
                suma_pesos = sum(t.peso for t in tipos)
                promedio = sum(n * t.peso/100 for t, n in zip([t[0] for t in notas_alumno], [t[1] for t in notas_alumno]))
                if forzar_reprobado and promedio >= 51:
                    factor = 50 / promedio
                    notas_alumno = [(tipo, round(max(0, min(50, n*factor)), 2)) for tipo, n in notas_alumno]
                elif not forzar_reprobado and promedio < 51:
                    factor = 52 / (promedio+1e-6)
                    notas_alumno = [(tipo, round(max(51, min(100, n*factor)), 2)) for tipo, n in notas_alumno]
                for tipo, calificacion in notas_alumno:
                    fecha_nota = fake.date_between_dates(date_start=fecha_evento_ini, date_end=fecha_evento_fin)
                    notas_bulk.append(Nota(
                        alumno=alumno,
                        tipo_nota=tipo,
                        materia_asignada=ma,
                        calificacion=calificacion,
                        fecha=fecha_nota
                    ))
                    notas_count += 1
                    if notas_count % batch_size == 0:
                        Nota.objects.bulk_create(notas_bulk)
                        print(f"Notas generadas: {notas_count}")
                        notas_bulk = []
                # Asistencias
                fechas_asistencia = []
                while len(fechas_asistencia) < 20:
                    mes = random.choice(meses_validos)
                    dia = random.randint(1, 28)
                    fecha = datetime.date(int(ciclo), mes, dia)
                    if fecha_evento_ini <= fecha <= fecha_evento_fin and fecha.weekday() in dias_validos:
                        fechas_asistencia.append(fecha)
                for fecha in fechas_asistencia:
                    estado = random.choices(['presente', 'ausente', 'justificado'], weights=[0.85, 0.1, 0.05])[0]
                    asistencias_bulk.append(Asistencia(
                        alumno=alumno,
                        materia_asignada=ma,
                        fecha=fecha,
                        estado=estado
                    ))
                    asistencias_count += 1
                    if asistencias_count % batch_size == 0:
                        Asistencia.objects.bulk_create(asistencias_bulk)
                        print(f"Asistencias generadas: {asistencias_count}")
                        asistencias_bulk = []
                # Participaciones
                fechas_participacion = []
                while len(fechas_participacion) < 10:
                    mes = random.choice(meses_validos)
                    dia = random.randint(1, 28)
                    fecha = datetime.date(int(ciclo), mes, dia)
                    if fecha_evento_ini <= fecha <= fecha_evento_fin and fecha.weekday() in dias_validos:
                        fechas_participacion.append(fecha)
                for fecha in fechas_participacion:
                    puntaje = round(max(0, min(10, random.gauss(7, 1.5))), 2)
                    participaciones_bulk.append(Participacion(
                        alumno=alumno,
                        materia_asignada=ma,
                        fecha=fecha,
                        puntaje=puntaje,
                        observacion=fake.sentence()
                    ))
                    participaciones_count += 1
                    if participaciones_count % batch_size == 0:
                        Participacion.objects.bulk_create(participaciones_bulk)
                        print(f"Participaciones generadas: {participaciones_count}")
                        participaciones_bulk = []
        if notas_bulk:
            Nota.objects.bulk_create(notas_bulk)
            print(f"Notas generadas: {notas_count}")
        if asistencias_bulk:
            Asistencia.objects.bulk_create(asistencias_bulk)
            print(f"Asistencias generadas: {asistencias_count}")
        if participaciones_bulk:
            Participacion.objects.bulk_create(participaciones_bulk)
            print(f"Participaciones generadas: {participaciones_count}")

    def exportar_credenciales_2025(self):
        alumnos_activos_2025 = set(Alumno.objects.filter(inscripciones__ciclo='2025', inscripciones__estado='activo').distinct())
        tutores_activos_2025 = set()
        for alumno in alumnos_activos_2025:
            tutores = Tutor.objects.filter(tutoralumno__alumno=alumno, tutoralumno__activo=True)
            tutores_activos_2025.update(tutores)
        maestros_activos_2025 = set(Maestro.objects.filter(materias_asignadas__ciclo='2025').distinct())
        usuarios_exportados = set()
        credenciales_exportar = []
        for alumno in alumnos_activos_2025:
            usuario = alumno.persona.usuario
            if usuario.username not in usuarios_exportados:
                credenciales_exportar.append({
                    'rol': 'Alumno',
                    'username': usuario.username,
                    'nombre': f"{alumno.persona.nombre} {alumno.persona.apellido_paterno} {alumno.persona.apellido_materno}",
                    'password': alumno.persona.ci
                })
                usuarios_exportados.add(usuario.username)
        for tutor in tutores_activos_2025:
            usuario = tutor.persona.usuario
            if usuario.username not in usuarios_exportados:
                credenciales_exportar.append({
                    'rol': 'Tutor',
                    'username': usuario.username,
                    'nombre': f"{tutor.persona.nombre} {tutor.persona.apellido_paterno} {tutor.persona.apellido_materno}",
                    'password': tutor.persona.ci
                })
                usuarios_exportados.add(usuario.username)
        for maestro in maestros_activos_2025:
            usuario = maestro.persona.usuario
            if usuario.username not in usuarios_exportados:
                credenciales_exportar.append({
                    'rol': 'Maestro',
                    'username': usuario.username,
                    'nombre': f"{maestro.persona.nombre} {maestro.persona.apellido_paterno} {maestro.persona.apellido_materno}",
                    'password': maestro.persona.ci
                })
                usuarios_exportados.add(usuario.username)
        cred_path = os.path.join(os.path.dirname(__file__), 'credenciales_creadas_2025.txt')
        with open(cred_path, 'w', encoding='utf-8') as f:
            for c in credenciales_exportar:
                f.write(f"Rol: {c['rol']} | Username: {c['username']} | Nombre: {c['nombre']} | Password: {c['password']}\n")
        print(f"Credenciales generadas guardadas en {cred_path}")