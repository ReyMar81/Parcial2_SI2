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
        # 1. Crear grados
        grados = [Grado.objects.get_or_create(nombre=gn, nivel='Secundaria')[0] for gn in GRADOS_SEC]
        # 2. Crear secciones
        secciones = [Seccion.objects.get_or_create(nombre=letra)[0] for letra in SECCION_LETRAS]
        # 3. Crear secciones_grado
        secciongrados = {}
        for grado in grados:
            for seccion in secciones:
                sg, _ = SeccionGrado.objects.get_or_create(grado=grado, seccion=seccion, aula=f'Aula {grado.nombre}-{seccion.nombre}', capacidad_maxima=40)
                secciongrados[(grado.nombre, seccion.nombre)] = sg
        # 4. Crear materias
        materias = [Materia.objects.get_or_create(nombre=nombre, descripcion=desc)[0] for nombre, desc in MATERIAS]
        # 5. Crear maestros
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
        # 6. Asignar materias a maestros por ciclo y sección_grado
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
                    # 7. Crear tipos de nota para cada asignación
                    for tipo in TIPOS_NOTA:
                        TipoNota.objects.get_or_create(materia_asignada=ma, nombre=tipo['nombre'], defaults={'peso': tipo['peso']})
        # 8. Inscribir 35 alumnos por sección en 2022 (total 70)
        alumnos = []
        tutores = []
        for seccion in secciones:
            for i in range(35):
                genero = random.choice(['M', 'F'])
                nombre = fake.first_name_male() if genero == 'M' else fake.first_name_female()
                persona_data = {
                    'nombre': nombre,
                    'apellido_paterno': fake.last_name(),
                    'apellido_materno': fake.last_name(),
                    'genero': genero,
                    'ci': f'ALUMNO{seccion.nombre}{i+1:05d}',
                    'direccion': fake.address(),
                    'contacto': f'+591 {random.randint(60000000,79999999)}',
                    'fecha_nacimiento': fake.date_of_birth(minimum_age=11, maximum_age=13)
                }
                alumno = crear_usuario_persona_rol(persona_data, rol='alumno', ciclo_anio=2022)
                # Tutor
                genero_t = random.choice(['M', 'F'])
                nombre_t = fake.first_name_male() if genero_t == 'M' else fake.first_name_female()
                tutor_data = {
                    'nombre': nombre_t,
                    'apellido_paterno': persona_data['apellido_paterno'],
                    'apellido_materno': persona_data['apellido_materno'],
                    'genero': genero_t,
                    'ci': f'TUTOR{seccion.nombre}{i+1:05d}',
                    'direccion': fake.address(),
                    'contacto': f'+591 {random.randint(60000000,79999999)}',
                    'fecha_nacimiento': fake.date_of_birth(minimum_age=30, maximum_age=60),
                    'ocupacion': fake.job()
                }
                tutor = crear_usuario_persona_rol(tutor_data, rol='tutor', ocupacion=tutor_data['ocupacion'])
                TutorAlumno.objects.get_or_create(tutor=tutor, alumno=alumno, defaults={'tipo_relacion': 'Padre/Madre', 'activo': True})
                alumnos.append((alumno, seccion))
                tutores.append(tutor)
                print(f"Alumno: {nombre} {persona_data['apellido_paterno']} {persona_data['apellido_materno']} | CI: {persona_data['ci']} | Usuario: {alumno.persona.usuario.username} | Contraseña: {alumno.persona.ci}")
                print(f"Tutor: {nombre_t} {persona_data['apellido_paterno']} {persona_data['apellido_materno']} | CI: {tutor_data['ci']}")
        # Asignar alumnos a secciones de 1ro (A y B)
        for alumno, seccion in alumnos:
            grado = grados[0]
            sg = secciongrados[(grado.nombre, seccion.nombre)]
            SeccionAlumno.objects.get_or_create(
                alumno=alumno,
                seccion_grado=sg,
                ciclo='2022',
                defaults={'fecha_inscripcion': datetime.date(2022, 2, 10), 'estado': 'activo'}
            )
        # 9. Asignar notas, asistencias y participaciones en 2022 con distribución coherente
        alumnos_por_seccion = {seccion.nombre: [] for seccion in secciones}
        for alumno, seccion in alumnos:
            alumnos_por_seccion[seccion.nombre].append(alumno)
        total_alumnos = len(alumnos)
        dias_habiles_2022 = dias_habiles_del_ano(2022, (3, 12))
        reprobados_2022 = {}
        for seccion in SECCION_LETRAS:
            # Elegir 1 o 2 reprobados por sección
            n_reprobados = random.choice([1, 2])
            reprobados_2022[seccion] = random.sample(alumnos_por_seccion[seccion], n_reprobados)
        for idx, (alumno, seccion) in enumerate(alumnos):
            grado = grados[0]
            sg = secciongrados[(grado.nombre, seccion.nombre)]
            es_reprobado = alumno in reprobados_2022[seccion.nombre]
            for materia in materias:
                ma = materia_asignada_map[("2022", materia.nombre, sg.id)]
                tipos = list(TipoNota.objects.filter(materia_asignada=ma))
                if es_reprobado:
                    # Trayectoria realista: tareas decentes, exámenes bajos, final muy bajo
                    notas = []
                    for tipo in tipos:
                        if "Examen Final" in tipo.nombre:
                            calificacion = round(random.uniform(20, 35), 2)
                        elif "Examen" in tipo.nombre:
                            calificacion = round(random.uniform(35, 55), 2)
                        elif "Exposición" in tipo.nombre:
                            calificacion = round(random.uniform(40, 60), 2)
                        else:
                            calificacion = round(random.uniform(50, 65), 2)
                        notas.append((tipo, calificacion))
                    for tipo, calificacion in notas:
                        Nota.objects.create(
                            alumno=alumno,
                            tipo_nota=tipo,
                            materia_asignada=ma,
                            calificacion=calificacion,
                            fecha=random.choice(dias_habiles_2022)
                        )
                else:
                    # Trayectorias normales/buenas
                    notas = []
                    for tipo in tipos:
                        if random.random() < 0.13:
                            calificacion = round(random.uniform(51, 65), 2)
                        elif idx < int(0.6 * total_alumnos):
                            calificacion = round(random.uniform(86, 100), 2)
                        else:
                            calificacion = round(random.uniform(66, 85), 2)
                        notas.append((tipo, calificacion))
                    for tipo, calificacion in notas:
                        Nota.objects.create(
                            alumno=alumno,
                            tipo_nota=tipo,
                            materia_asignada=ma,
                            calificacion=calificacion,
                            fecha=random.choice(dias_habiles_2022)
                        )
                # Asistencias: una por cada día hábil
                asistencias_bulk = []
                for fecha in dias_habiles_2022:
                    estado = random.choices(['presente', 'ausente', 'justificado'], weights=[0.85, 0.1, 0.05])[0]
                    asistencias_bulk.append(Asistencia(
                        alumno=alumno,
                        materia_asignada=ma,
                        fecha=fecha,
                        estado=estado
                    ))
                Asistencia.objects.bulk_create(asistencias_bulk)
                # Participaciones: solo algunos días
                participaciones_bulk = []
                for fecha in dias_habiles_2022:
                    if random.random() < 0.25:
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
        # 10. Calcular resultados finales y reinscribir aprobados según materias
        alumnos_por_ciclo = {'2022': [(alumno, seccion) for alumno, seccion in alumnos if alumno not in reprobados_2022[seccion.nombre]]}
        for ciclo_idx, ciclo in enumerate(CICLOS[1:]):
            prev_ciclo = CICLOS[ciclo_idx]
            nuevos_alumnos = []
            prev_alumnos = alumnos_por_ciclo[prev_ciclo]
            # Agrupar por sección
            alumnos_por_seccion = {seccion.nombre: [] for seccion in secciones}
            for alumno, seccion in prev_alumnos:
                alumnos_por_seccion[seccion.nombre].append(alumno)
            meses_hasta = 6 if ciclo == '2025' else 12
            aprobados_ciclo = []
            # --- PRIMERO INSCRIBIR A TODOS LOS APROBADOS DEL CICLO ANTERIOR ---
            inscritos_ciclo = []
            for idx, (alumno, seccion) in enumerate(prev_alumnos):
                grado_idx = ciclo_idx + 1
                if grado_idx < len(grados):
                    grado = grados[grado_idx]
                    sg = secciongrados[(grado.nombre, seccion.nombre)]
                    # Inscribir a todos los que llegan a este ciclo
                    SeccionAlumno.objects.get_or_create(
                        alumno=alumno,
                        seccion_grado=sg,
                        ciclo=ciclo,
                        defaults={'fecha_inscripcion': datetime.date(int(ciclo), 2, 10), 'estado': 'activo'}
                    )
                    inscritos_ciclo.append((alumno, seccion))
            # --- LUEGO SELECCIONAR REPROBADOS ENTRE LOS INSCRITOS ---
            reprobados_ciclo = {}
            materias_reprobar_por_alumno = {}
            if ciclo != '2025':
                for seccion in SECCION_LETRAS:
                    alumnos_seccion = [al for al, sec in inscritos_ciclo if sec.nombre == seccion]
                    n_reprobados = random.choice([1, 2]) if len(alumnos_seccion) > 2 else 1 if len(alumnos_seccion) == 2 else 0
                    reprobados = random.sample(alumnos_seccion, n_reprobados) if n_reprobados > 0 else []
                    reprobados_ciclo[seccion] = reprobados
                    for alumno in reprobados:
                        n_mat_reprobar = random.choice([1, 2])
                        materias_reprobar_por_alumno[alumno.id] = set(random.sample([m.nombre for m in materias], n_mat_reprobar))
            # --- ASIGNACIÓN DE NOTAS DESPUÉS DE SELECCIÓN DE REPROBADOS ---
            for idx, (alumno, seccion) in enumerate(inscritos_ciclo):
                grado_idx = ciclo_idx + 1
                if grado_idx < len(grados):
                    grado = grados[grado_idx]
                    sg = secciongrados[(grado.nombre, seccion.nombre)]
                    promedios_materias = []
                    for materia in materias:
                        ma = materia_asignada_map[(ciclo, materia.nombre, sg.id)]
                        tipos = list(TipoNota.objects.filter(materia_asignada=ma))
                        notas = []
                        if ciclo == '2025':
                            # Solo Tarea 1 y Tarea 2, en orden
                            for tipo in tipos:
                                if tipo.nombre == 'Tarea 1' or tipo.nombre == 'Tarea 2':
                                    calificacion = round(random.uniform(40, 95), 2)
                                    notas.append((tipo, calificacion))
                        elif alumno in reprobados_ciclo.get(seccion.nombre, []) and materia.nombre in materias_reprobar_por_alumno.get(alumno.id, set()):
                            # Depuración: mostrar alumno, materia y ciclo reprobados
                            print(f"[REPROBADO] Ciclo: {ciclo} | Sección: {seccion.nombre} | Alumno: {alumno.persona.nombre} {alumno.persona.apellido_paterno} | Materia: {materia.nombre}")
                            for tipo in tipos:
                                if "Examen Final" in tipo.nombre:
                                    calificacion = round(random.uniform(20, 45), 2)
                                elif "Examen" in tipo.nombre:
                                    calificacion = round(random.uniform(35, 55), 2)
                                elif "Exposición" in tipo.nombre:
                                    calificacion = round(random.uniform(40, 55), 2)
                                else:
                                    calificacion = round(random.uniform(30, 55), 2)
                                print(f"    Tipo: {tipo.nombre} | Nota: {calificacion}")
                                notas.append((tipo, calificacion))
                        elif alumno in reprobados_ciclo.get(seccion.nombre, []):
                            for tipo in tipos:
                                calificacion = round(random.uniform(51, 69), 2)
                                notas.append((tipo, calificacion))
                        else:
                            for tipo in tipos:
                                calificacion = round(random.uniform(66, 100), 2)
                                notas.append((tipo, calificacion))
                        for tipo, calificacion in notas:
                            Nota.objects.create(
                                alumno=alumno,
                                tipo_nota=tipo,
                                materia_asignada=ma,
                                calificacion=calificacion,
                                fecha=random.choice(dias_habiles_del_ano(int(ciclo), (3, meses_hasta)))
                            )
                        if ciclo != '2025':
                            notas_materia = Nota.objects.filter(alumno=alumno, materia_asignada=ma)
                            total = 0
                            peso_total = 0
                            for nota in notas_materia:
                                peso = nota.tipo_nota.peso
                                total += nota.calificacion * peso
                                peso_total += peso
                            promedio = total / peso_total if peso_total > 0 else 0
                            promedios_materias.append(promedio)
                    if ciclo != '2025' and all(pm >= 51 for pm in promedios_materias):
                        nuevos_alumnos.append((alumno, seccion))
            if ciclo != '2025':
                alumnos_por_ciclo[ciclo] = nuevos_alumnos
            else:
                alumnos_por_ciclo[ciclo] = inscritos_ciclo
            # 11. Registrar asistencias y participaciones (2025 solo hasta mayo)
            for idx, (alumno, seccion) in enumerate(alumnos_por_ciclo[ciclo]):
                grado_idx = ciclo_idx + 1
                if grado_idx < len(grados):
                    grado = grados[grado_idx]
                    sg = secciongrados[(grado.nombre, seccion.nombre)]
                    for materia in materias:
                        ma = materia_asignada_map[(ciclo, materia.nombre, sg.id)]
                        dias_habiles = dias_habiles_del_ano(int(ciclo), (3, meses_hasta))
                        asistencias_bulk = []
                        for fecha in dias_habiles:
                            estado = random.choices(['presente', 'ausente', 'justificado'], weights=[0.85, 0.1, 0.05])[0]
                            asistencias_bulk.append(Asistencia(
                                alumno=alumno,
                                materia_asignada=ma,
                                fecha=fecha,
                                estado=estado
                            ))
                        Asistencia.objects.bulk_create(asistencias_bulk)
                        participaciones_bulk = []
                        for fecha in dias_habiles:
                            if random.random() < 0.25:
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