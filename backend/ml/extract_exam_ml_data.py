import os
import django
import pandas as pd
from django.db.models import Avg, Q
from datetime import datetime

# Configura el entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.evaluacion.models import Nota, Asistencia, Participacion
from apps.materias.models import MateriaAsignada

# Configuración
CICLOS = ['2022', '2023', '2024']
TIPOS_NOTA = ['Tarea', 'Examen', 'Exposicion', 'Proyecto']  # Ajusta según tus tipos
# Orden manual de tipos de nota (ajusta si agregas más tipos)
ORDEN_TIPOS_NOTA = [
    "Tarea 1", "Tarea 2", "Tarea 3", "Tarea 4", "Examen 1", "Tarea 5", "Exposición", "Examen 2", "Tarea 6", "Tarea 7", "Examen Final"
]

# Extraer datos para ML orientado a predicción de exámenes
# target_tipo: tipo de nota a predecir (por ejemplo, 'Examen')
# target_num: número de la nota a predecir (por ejemplo, 1 para Examen_1)
def extraer_datos_ml_examenes(target_tipo='Examen 1', target_num=1):
    data = []
    all_columns = set()
    for ciclo in CICLOS:
        materias_asignadas = MateriaAsignada.objects.filter(ciclo=ciclo)
        for ma in materias_asignadas:
            # Obtener tipos de nota de la materia asignada, ordenados
            tipos_nota_objs = ma.tipos_nota.order_by('orden', 'id')
            tipos_nota_nombres = [tn.nombre for tn in tipos_nota_objs]
            # Contar cuántas veces aparece cada tipo de nota (por nombre)
            tipo_max_count = {nombre: 0 for nombre in tipos_nota_nombres}
            # Buscar el máximo número de cada tipo de nota entre todos los alumnos
            alumnos = Nota.objects.filter(materia_asignada=ma).values_list('alumno', flat=True).distinct()
            for alumno_id in alumnos:
                notas = Nota.objects.filter(alumno_id=alumno_id, materia_asignada=ma)
                for nombre in tipos_nota_nombres:
                    count = notas.filter(tipo_nota__nombre=nombre).count()
                    if count > tipo_max_count[nombre]:
                        tipo_max_count[nombre] = count
            # Generar todas las columnas posibles
            note_columns = []
            for nombre, max_count in tipo_max_count.items():
                for i in range(1, max_count+1):
                    col = f'{nombre}_{i}'
                    note_columns.append(col)
                    all_columns.add(col)
            # Ahora sí, por cada alumno, extraer features
            for alumno_id in alumnos:
                notas = Nota.objects.filter(alumno_id=alumno_id, materia_asignada=ma).order_by('fecha')
                features = {
                    'alumno_id': alumno_id,
                    'materia_asignada_id': ma.id,
                    'materia': ma.materia.nombre,
                    'ciclo': ciclo
                }
                for col in note_columns:
                    features[col] = None
                target_nota = None
                fecha_examen_objetivo = None
                # Determinar el índice del examen objetivo en la lista de orden
                if target_tipo not in ORDEN_TIPOS_NOTA:
                    # Buscar el tipo de nota objetivo por patrón y número de aparición (por fecha)
                    tipos_objetivo = [n for n in tipos_nota_nombres if target_tipo.lower() in n.lower()]
                    if not tipos_objetivo or len(tipos_objetivo) < target_num:
                        continue  # No hay suficientes coincidencias
                    nombre_objetivo = tipos_objetivo[target_num-1]
                    # Buscar la nota target y su fecha según aparición cronológica
                    notas_objetivo = list(notas.filter(tipo_nota__nombre=nombre_objetivo).order_by('fecha'))
                    if len(notas_objetivo) < 1:
                        continue
                    if len(notas_objetivo) < target_num:
                        continue
                    nota_target_obj = notas_objetivo[target_num-1]
                    target_nota = nota_target_obj.calificacion
                    fecha_examen_objetivo = nota_target_obj.fecha
                    # Incluir como features todas las notas previas (de cualquier tipo) a la fecha del examen objetivo
                    for nombre in tipos_nota_nombres:
                        notas_tipo = list(notas.filter(tipo_nota__nombre=nombre, fecha__lt=fecha_examen_objetivo).order_by('fecha'))
                        for idx, n in enumerate(notas_tipo, 1):
                            features[f'{nombre}_{idx}'] = n.calificacion
                else:
                    idx_examen = ORDEN_TIPOS_NOTA.index(target_tipo)
                    # Llenar las columnas de notas previas (de cualquier tipo) antes del examen objetivo
                    for nombre in tipos_nota_nombres:
                        if nombre not in ORDEN_TIPOS_NOTA:
                            continue
                        idx_nota = ORDEN_TIPOS_NOTA.index(nombre)
                        notas_tipo = list(notas.filter(tipo_nota__nombre=nombre).order_by('fecha'))
                        for idx, n in enumerate(notas_tipo, 1):
                            # Solo incluir notas previas al examen objetivo (por orden)
                            if idx_nota < idx_examen:
                                features[f'{nombre}_{idx}'] = n.calificacion
                            # Guardar la nota target y su fecha
                            if nombre == nombre_objetivo and idx == 1:
                                target_nota = n.calificacion
                                fecha_examen_objetivo = n.fecha
                # Asistencia y participación SOLO hasta la fecha del examen objetivo
                if fecha_examen_objetivo:
                    asistencias = Asistencia.objects.filter(
                        alumno_id=alumno_id,
                        materia_asignada=ma,
                        fecha__lt=fecha_examen_objetivo
                    )
                    total_asistencias = asistencias.count()
                    presentes = asistencias.filter(estado='presente').count()
                    porcentaje_asistencia = presentes / total_asistencias if total_asistencias else 0
                    participaciones = Participacion.objects.filter(
                        alumno_id=alumno_id,
                        materia_asignada=ma,
                        fecha__lt=fecha_examen_objetivo
                    )
                    promedio_participacion = participaciones.aggregate(avg=Avg('puntaje'))['avg'] or 0
                else:
                    porcentaje_asistencia = 0
                    promedio_participacion = 0
                features['porcentaje_asistencia'] = porcentaje_asistencia
                features['promedio_participacion'] = promedio_participacion
                features['target_nota'] = target_nota
                if target_nota is not None:
                    data.append(features)
    # Ordenar columnas
    base_cols = ['alumno_id', 'materia_asignada_id', 'materia', 'ciclo']
    note_cols_sorted = sorted(list(all_columns), key=lambda x: (x.split('_')[0], int(x.split('_')[1]) if x.split('_')[1].isdigit() else 0))
    final_cols = base_cols + note_cols_sorted + ['porcentaje_asistencia', 'promedio_participacion', 'target_nota']
    df = pd.DataFrame(data)
    df = df.reindex(columns=final_cols)
    df.to_csv('ml/datos_ml_examenes.csv', index=False)
    print(f"Datos exportados a ml/datos_ml_examenes.csv. Total registros: {len(df)}")

def listar_tipos_nota_unicos():
    from apps.materias.models import TipoNota
    nombres = TipoNota.objects.values_list('nombre', flat=True).distinct()
    print('Tipos de nota únicos en la base de datos:')
    for n in nombres:
        print(f'- {n}')

if __name__ == '__main__':
    # Para ver los tipos de nota disponibles, descomenta la siguiente línea:
    # listar_tipos_nota_unicos()
    # Ejemplo de uso para extraer datos de un examen específico:
    # extraer_datos_ml_examenes(target_tipo='Examen 1', target_num=1)
    # extraer_datos_ml_examenes(target_tipo='Examen 2', target_num=1)
    # extraer_datos_ml_examenes(target_tipo='Examen Final', target_num=1)
    extraer_datos_ml_examenes(target_tipo='Examen', target_num=1)
