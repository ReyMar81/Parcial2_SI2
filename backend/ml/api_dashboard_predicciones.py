from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.materias.models import MateriaAsignada
from apps.personas.models import Alumno
from apps.evaluacion.models import Nota
from django.contrib.auth import get_user_model
import joblib
import numpy as np
import pandas as pd
from apps.secciones.models import SeccionAlumno
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

class DashboardMateriasPrediccionesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ciclo",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtrar por ciclo escolar (ej: 2025)"
            )
        ],
        description="Devuelve el resumen de predicciones ML por materia para el ciclo especificado (o todos si no se especifica ciclo)."
    )
    def get(self, request):
        user = request.user
        ciclo = request.query_params.get('ciclo')
        # Si es superusuario, mostrar todas las materias (opcionalmente filtrar por ciclo)
        if user.is_superuser:
            materias = MateriaAsignada.objects.all()
        else:
            materias = MateriaAsignada.objects.filter(maestro__persona__usuario=user)
        if ciclo:
            materias = materias.filter(ciclo=ciclo)
        model = joblib.load('ml/modelo_random_forest_clf.pkl')
        resumen = []
        if not materias.exists():
            materias = [type('DummyMateria', (), {
                'id': 1,
                'materia': type('DummyMateriaObj', (), {'nombre': 'Materia Demo'})(),
                'seccion_grado': None,
                'ciclo': ciclo or '2025',
            })()]
        for materia in materias:
            alumnos_qs = SeccionAlumno.objects.filter(
                seccion_grado=getattr(materia, 'seccion_grado', None),
                ciclo=getattr(materia, 'ciclo', ciclo or '2025'),
                estado='activo'
            )
            alumnos = [sa.alumno for sa in alumnos_qs]
            total = len(alumnos)
            aprobados = 0
            en_riesgo = 0
            for alumno in alumnos:
                notas = Nota.objects.filter(alumno=alumno, materia_asignada=materia)
                features = {
                    'Examen 1_1': 80, 'Examen 2_1': 70, 'Examen Final_1': 75, 'Exposición_1': 85,
                    'Tarea 1_1': 90, 'Tarea 2_1': 80, 'Tarea 3_1': 85, 'Tarea 4_1': 70, 'Tarea 5_1': 95, 'Tarea 6_1': 80, 'Tarea 7_1': 90,
                    'cantidad_participaciones': 5, 'porcentaje_participacion': 0.8, 'promedio_participacion': 0.7, 'porcentaje_asistencia': 0.9
                }
                for n in notas:
                    nombre = n.tipo_nota.nombre
                    key = f'{nombre}_1'
                    if key in features:
                        features[key] = n.calificacion or 0
                X = pd.DataFrame([features])
                try:
                    pred = model.predict(X)[0]
                except Exception:
                    pred = 0
                if pred:
                    aprobados += 1
                else:
                    en_riesgo += 1
            resumen.append({
                'materia_id': getattr(materia, 'id', 0),
                'materia_nombre': getattr(materia.materia, 'nombre', 'Materia Demo'),
                'total_alumnos': total,
                'aprobados': aprobados,
                'en_riesgo': en_riesgo,
                'porcentaje_aprobados': round((aprobados/total)*100, 1) if total else 0,
                'porcentaje_en_riesgo': round((en_riesgo/total)*100, 1) if total else 0
            })
        return Response(resumen)
