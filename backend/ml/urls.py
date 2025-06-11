from django.urls import path
from .api_predict_exam import PredecirAprobadoExamenAPIView
from .api_predict_materia import PredecirAprobadoMateriaAPIView

urlpatterns = [
    path('predict-exam/', PredecirAprobadoExamenAPIView.as_view(), name='predict-exam'),
    path('predict-materia/', PredecirAprobadoMateriaAPIView.as_view(), name='predict-materia'),
]
