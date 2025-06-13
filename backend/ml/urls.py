from django.urls import path
from .api_predict_exam import PredecirAprobadoExamenAPIView
from .api_predict_materia import PredecirAprobadoMateriaAPIView
from .api_dashboard_predicciones import DashboardMateriasPrediccionesAPIView

urlpatterns = [
    path('predict-exam/', PredecirAprobadoExamenAPIView.as_view(), name='predict-exam'),
    path('predict-materia/', PredecirAprobadoMateriaAPIView.as_view(), name='predict-materia'),
    path('dashboard-materias-predicciones/', DashboardMateriasPrediccionesAPIView.as_view(), name='dashboard-materias-predicciones'),
]
