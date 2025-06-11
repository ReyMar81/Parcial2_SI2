import joblib
import numpy as np
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

class PredecirAprobadoMateriaAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """
        Recibe: features (dict con todos los features requeridos por el modelo ML)
        Devuelve: {'aprobado': 1/0, 'probabilidad': float, 'features': dict}
        """
        data = request.data
        # Lista de features requeridos por el modelo (ajusta según tu entrenamiento)
        REQUIRED_FEATURES = [
            'Tarea 1', 'Tarea 2', 'Examen 1', 'cantidad_participaciones',
            'promedio_participacion', 'porcentaje_asistencia', 'promedio_nota'
            # ...agrega aquí todos los features esperados por el modelo
        ]
        # Validar que todos los features requeridos estén presentes y sean numéricos
        missing = [f for f in REQUIRED_FEATURES if f not in data]
        if missing:
            return Response({'error': f'Faltan features requeridos: {missing}'}, status=400)
        try:
            features = [float(data[f]) for f in REQUIRED_FEATURES]
        except Exception as e:
            return Response({'error': f'Error de formato en features: {str(e)}'}, status=400)
        model = joblib.load('ml/modelo_random_forest_clf.pkl')
        X = np.array([features])
        try:
            pred = model.predict(X)[0]
            prob = float(model.predict_proba(X)[0][1])
        except Exception as e:
            return Response({'error': 'Error en predicción ML', 'detalle': str(e)}, status=500)
        return Response({
            'aprobado': int(pred),
            'probability': prob,
            'features': {f: data[f] for f in REQUIRED_FEATURES}
        })
