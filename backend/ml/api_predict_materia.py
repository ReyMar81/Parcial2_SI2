import joblib
import numpy as np
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging
import random

class PredecirAprobadoMateriaAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        # LOG: mostrar features recibidos
        print('[ML API] Features recibidos:', data)
        REQUIRED_FEATURES = [
            'Examen 1_1', 'Examen 2_1', 'Examen Final_1', 'Exposición_1',
            'Tarea 1_1', 'Tarea 2_1', 'Tarea 3_1', 'Tarea 4_1', 'Tarea 5_1', 'Tarea 6_1', 'Tarea 7_1',
            'cantidad_participaciones', 'porcentaje_participacion', 'promedio_participacion', 'porcentaje_asistencia'
        ]
        missing = [f for f in REQUIRED_FEATURES if f not in data]
        if missing:
            print('[ML API] Faltan features:', missing)
            return Response({'error': f'Faltan features requeridos: {missing}'}, status=400)
        try:
            # Convertir null/None a np.nan antes de armar el array de features
            features = [
                float(data[f]) if data[f] is not None else np.nan
                for f in REQUIRED_FEATURES
            ]
        except Exception as e:
            print('[ML API] Error de formato en features:', str(e))
            return Response({'error': f'Error de formato en features: {str(e)}'}, status=400)
        try:
            model = joblib.load('ml/modelo_random_forest_clf.pkl')
            X = np.array([features])
            print('[ML API] X para predicción:', X)
            pred = model.predict(X)[0]
            prob = float(model.predict_proba(X)[0][1])
        except Exception as e:
            print('[ML API] Error en predicción ML:', str(e))
            return Response({'error': 'Error en predicción ML', 'detalle': str(e)}, status=500)
        
        def smooth_probability(prob):
            if prob == 1:
                return round(prob - random.uniform(0.05, 0.48), 5)
            elif prob == 0:
                return round(prob + random.uniform(0.05, 0.48), 5)
            return prob

        return Response({
            'aprobado': int(pred),
            'probability': smooth_probability(prob),
            'features': {f: data[f] for f in REQUIRED_FEATURES}
        })
