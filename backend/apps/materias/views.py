from rest_framework import viewsets
from apps.materias.models import Materia, MateriaAsignada, ResultadoFinalMateria, TipoNota
from apps.materias.serializers import MateriaSerializer, MateriaAsignadaSerializer, ResultadoFinalMateriaSerializer, TipoNotaSerializer

class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer

class MateriaAsignadaViewSet(viewsets.ModelViewSet):
    queryset = MateriaAsignada.objects.all()
    serializer_class = MateriaAsignadaSerializer

class TipoNotaViewSet(viewsets.ModelViewSet):
    queryset = TipoNota.objects.all()
    serializer_class = TipoNotaSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        materia_asignada = request.data.get('materia_asignada')
        if materia_asignada:
            tipos = TipoNota.objects.filter(materia_asignada=materia_asignada)
            suma = sum([t.peso for t in tipos])
            if suma > 100:
                response.data['warning'] = "La suma de los pesos de las notas supera el 100%. Se recomienda ajustar los valores."
            elif suma < 100:
                response.data['info'] = "La suma de los pesos de las notas es menor al 100%. El promedio se calculará sobre el porcentaje definido."
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        materia_asignada = request.data.get('materia_asignada')
        if materia_asignada:
            tipos = TipoNota.objects.filter(materia_asignada=materia_asignada)
            suma = sum([t.peso for t in tipos])
            if suma > 100:
                response.data['warning'] = "La suma de los pesos de las notas supera el 100%. Se recomienda ajustar los valores."
            elif suma < 100:
                response.data['info'] = "La suma de los pesos de las notas es menor al 100%. El promedio se calculará sobre el porcentaje definido."
        return response
    
class ResultadoFinalMateriaViewSet(viewsets.ModelViewSet):
    queryset = ResultadoFinalMateria.objects.all()
    serializer_class = ResultadoFinalMateriaSerializer
