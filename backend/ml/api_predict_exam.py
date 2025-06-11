import joblib
import pandas as pd
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import os
from apps.evaluacion.models import Nota, Asistencia, Participacion
from apps.materias.models import MateriaAsignada
from apps.personas.models import Alumno

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'modelo_random_forest_examen_clf.pkl')

class PredecirAprobadoExamenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Espera ciclo, materia_asignada, alumno, tipo_examen
        ciclo = request.data.get('ciclo')
        materia_asignada = request.data.get('materia_asignada')
        alumno = request.data.get('alumno')
        tipo_examen = request.data.get('tipo_examen')  # Ej: 'Examen 1'
        if not (ciclo and materia_asignada and alumno and tipo_examen):
            return JsonResponse({'error': 'Faltan datos requeridos (ciclo, materia_asignada, alumno, tipo_examen)'}, status=400)

        # Obtener todas las notas previas a ese examen para ese alumno y materia_asignada
        notas_previas = Nota.objects.filter(
            alumno_id=alumno,
            materia_asignada_id=materia_asignada,
            materia_asignada__ciclo=ciclo
        ).order_by('tipo_nota__orden', 'fecha')

        # Construir features: solo notas previas al tipo_examen
        # Orden fijo esperado para features ML
        ORDEN_TIPOS_NOTA = [
            "Tarea 1", "Tarea 2", "Tarea 3", "Tarea 4", "Examen 1", "Tarea 5", "Exposición", "Examen 2", "Tarea 6", "Tarea 7", "Examen Final"
        ]
        features = {}
        # Determinar el índice del examen objetivo
        try:
            idx_examen = ORDEN_TIPOS_NOTA.index(tipo_examen)
        except ValueError:
            return JsonResponse({'error': f'Tipo de examen {tipo_examen} no válido'}, status=400)
        # Para cada tipo de nota previa al examen, tomar la nota del alumno (o 0 si no existe)
        for nombre in ORDEN_TIPOS_NOTA:
            if nombre == tipo_examen:
                break
            nota = notas_previas.filter(tipo_nota__nombre=nombre).order_by('fecha').first()
            features[f'{nombre}_1'] = nota.calificacion if nota else 0
        # Asegurar que todos los features usados en el entrenamiento estén presentes
        for nombre in ORDEN_TIPOS_NOTA:
            if f'{nombre}_1' not in features:
                features[f'{nombre}_1'] = 0
        # Asistencia y participación reales hasta la fecha del examen (si existen)
        examen_obj = Nota.objects.filter(
            alumno_id=alumno,
            materia_asignada_id=materia_asignada,
            materia_asignada__ciclo=ciclo,
            tipo_nota__nombre=tipo_examen
        ).order_by('fecha').first()
        if examen_obj:
            fecha_examen = examen_obj.fecha
            asistencias = Asistencia.objects.filter(
                alumno_id=alumno,
                materia_asignada_id=materia_asignada,
                fecha__lt=fecha_examen
            )
            total_asistencias = asistencias.count()
            presentes = asistencias.filter(estado='presente').count()
            porcentaje_asistencia = presentes / total_asistencias if total_asistencias else 0
            participaciones = Participacion.objects.filter(
                alumno_id=alumno,
                materia_asignada_id=materia_asignada,
                fecha__lt=fecha_examen
            )
            promedio_participacion = participaciones.aggregate(avg=pd.models.Avg('puntaje'))['avg'] or 0
        else:
            porcentaje_asistencia = 0
            promedio_participacion = 0
        features['porcentaje_asistencia'] = porcentaje_asistencia
        features['promedio_participacion'] = promedio_participacion
        # Cargar modelo y predecir
        model = joblib.load(MODEL_PATH)
        # Orden correcto de features según el entrenamiento y el CSV
        ordered_features = [
            'Examen 1_1', 'Examen 2_1', 'Examen Final_1', 'Exposición_1',
            'Tarea 1_1', 'Tarea 2_1', 'Tarea 3_1', 'Tarea 4_1',
            'Tarea 5_1', 'Tarea 6_1', 'Tarea 7_1',
            'porcentaje_asistencia', 'promedio_participacion'
        ]
        X = pd.DataFrame([[features.get(col, 0) for col in ordered_features]], columns=ordered_features)
        print('ML DEBUG - ordered_features:', ordered_features)
        print('ML DEBUG - X DataFrame:', X)
        try:
            pred = model.predict(X)[0]
            prob = model.predict_proba(X)[0][1]
        except Exception as e:
            import traceback
            print('ML DEBUG - ERROR en predicción:', str(e))
            traceback.print_exc()
            return JsonResponse({'error': 'Error en predicción ML', 'detalle': str(e)}, status=500)
        return JsonResponse({'aprobado': int(pred), 'probabilidad_aprobado': float(prob)})
