from rest_framework import viewsets
from apps.evaluacion.models import Nota, Asistencia, Participacion
from apps.evaluacion.serializers import NotaSerializer, AsistenciaSerializer, ParticipacionSerializer

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer

class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer

class ParticipacionViewSet(viewsets.ModelViewSet):
    queryset = Participacion.objects.all()
    serializer_class = ParticipacionSerializer