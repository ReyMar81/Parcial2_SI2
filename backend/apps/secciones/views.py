from rest_framework import viewsets
from apps.secciones.models import Grado, Seccion, SeccionAlumno, ResultadoFinalSeccion
from apps.secciones.serializers import GradoSerializer, SeccionSerializer, SeccionAlumnoSerializer, ResultadoFinalSeccionSerializer

class GradoViewSet(viewsets.ModelViewSet):
    queryset = Grado.objects.all()
    serializer_class = GradoSerializer

class SeccionViewSet(viewsets.ModelViewSet):
    queryset = Seccion.objects.all()
    serializer_class = SeccionSerializer

class SeccionAlumnoViewSet(viewsets.ModelViewSet):
    queryset = SeccionAlumno.objects.all()
    serializer_class = SeccionAlumnoSerializer

class ResultadoFinalSeccionViewSet(viewsets.ModelViewSet):
    queryset = ResultadoFinalSeccion.objects.all()
    serializer_class = ResultadoFinalSeccionSerializer