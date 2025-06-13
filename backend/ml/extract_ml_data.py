import os
import django
import pandas as pd
from django.db.models import Avg
from datetime import timedelta

# Configura el entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.evaluacion.models import Nota, Asistencia, Participacion
from apps.materias.models import MateriaAsignada, TipoNota

# Configuración
CICLOS = ['2022', '2023', '2024', '2025']

# Extraer datos para ML (materia): incluye todas las notas por tipo, cantidad y promedio de participaciones, asistencia

def extraer_datos_ml():
    data = []
    all_note_columns = set()
    for ciclo in CICLOS:
        materias_asignadas = MateriaAsignada.objects.filter(ciclo=ciclo)
        for ma in materias_asignadas:
            # Obtener todos los tipos de nota definidos para la materia asignada (ordenados)
            tipos_nota_objs = ma.tipos_nota.order_by('orden', 'id')
            tipos_nota_nombres = [tn.nombre for tn in tipos_nota_objs]
            # Buscar el máximo número de cada tipo de nota entre todos los alumnos
            tipo_max_count = {nombre: 0 for nombre in tipos_nota_nombres}
            alumnos = Nota.objects.filter(materia_asignada=ma).values_list('alumno', flat=True).distinct()
            for alumno_id in alumnos:
                notas = Nota.objects.filter(alumno_id=alumno_id, materia_asignada=ma)
                for nombre in tipos_nota_nombres:
                    count = notas.filter(tipo_nota__nombre=nombre).count()
                    if count > tipo_max_count[nombre]:
                        tipo_max_count[nombre] = count
            # Generar todas las columnas posibles para las notas
            note_columns = []
            for nombre, max_count in tipo_max_count.items():
                for i in range(1, max_count+1):
                    col = f'{nombre}_{i}'
                    note_columns.append(col)
                    all_note_columns.add(col)
            # Por cada alumno, extraer features
            for alumno_id in alumnos:
                notas = Nota.objects.filter(alumno_id=alumno_id, materia_asignada=ma).order_by('fecha')
                if not notas.exists():
                    continue
                fechas_corte = [n.fecha for n in notas]
                for corte_idx, fecha_corte in enumerate(fechas_corte):
                    features = {
                        'alumno_id': alumno_id,
                        'materia_asignada_id': ma.id,
                        'materia': ma.materia.nombre,
                        'ciclo': ciclo
                    }
                    # Notas por tipo
                    for col in note_columns:
                        features[col] = None
                    for nombre in tipos_nota_nombres:
                        notas_tipo = list(notas.filter(tipo_nota__nombre=nombre, fecha__lte=fecha_corte).order_by('fecha'))
                        for idx, n in enumerate(notas_tipo, 1):
                            features[f'{nombre}_{idx}'] = n.calificacion
                    # Participaciones hasta la fecha de corte
                    participaciones = Participacion.objects.filter(alumno_id=alumno_id, materia_asignada=ma, fecha__lte=fecha_corte)
                    cantidad_participaciones = participaciones.count()
                    # Porcentaje de participación: cantidad_participaciones / cantidad de clases hasta la fecha
                    # Suponemos que cada día con nota o asistencia es una clase
                    clases_hasta_fecha = set(list(Nota.objects.filter(alumno_id=alumno_id, materia_asignada=ma, fecha__lte=fecha_corte).values_list('fecha', flat=True)) + list(Asistencia.objects.filter(alumno_id=alumno_id, materia_asignada=ma, fecha__lte=fecha_corte).values_list('fecha', flat=True)))
                    total_clases = len(clases_hasta_fecha)
                    porcentaje_participacion = cantidad_participaciones / total_clases if total_clases else 0
                    promedio_participacion = participaciones.aggregate(avg=Avg('puntaje'))['avg'] or 0
                    # Asistencias hasta la fecha de corte
                    asistencias = Asistencia.objects.filter(alumno_id=alumno_id, materia_asignada=ma, fecha__lte=fecha_corte)
                    total_asistencias = asistencias.count()
                    presentes = asistencias.filter(estado='presente').count()
                    porcentaje_asistencia = presentes / total_asistencias if total_asistencias else 0
                    # Notas hasta la fecha de corte
                    notas_hasta_corte = notas.filter(fecha__lte=fecha_corte)
                    promedio_nota = notas_hasta_corte.aggregate(avg=Avg('calificacion'))['avg'] or 0
                    # Target: aprobado al final del ciclo (usando todas las notas)
                    notas_finales = Nota.objects.filter(alumno_id=alumno_id, materia_asignada=ma)
                    promedio_nota_final = notas_finales.aggregate(avg=Avg('calificacion'))['avg'] or 0
                    aprobado = 1 if promedio_nota_final >= 51 else 0
                    features['cantidad_participaciones'] = cantidad_participaciones
                    features['porcentaje_participacion'] = porcentaje_participacion
                    features['promedio_participacion'] = promedio_participacion
                    features['porcentaje_asistencia'] = porcentaje_asistencia
                    features['promedio_nota'] = promedio_nota
                    features['aprobado'] = aprobado
                    features['fecha_corte'] = fecha_corte
                    data.append(features)
    # Ordenar columnas
    base_cols = ['alumno_id', 'materia_asignada_id', 'materia', 'ciclo', 'fecha_corte']
    note_cols_sorted = sorted(list(all_note_columns), key=lambda x: (x.split('_')[0], int(x.split('_')[1]) if x.split('_')[1].isdigit() else 0))
    final_cols = base_cols + note_cols_sorted + [
        'cantidad_participaciones', 'porcentaje_participacion', 'promedio_participacion', 'porcentaje_asistencia', 'promedio_nota', 'aprobado'
    ]
    df = pd.DataFrame(data)
    df = df.reindex(columns=final_cols)
    df.to_csv('ml/datos_ml.csv', index=False)
    print(f"Datos exportados a ml/datos_ml.csv. Total registros: {len(df)}")

if __name__ == '__main__':
    extraer_datos_ml()
