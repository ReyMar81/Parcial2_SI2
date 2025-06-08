from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from apps.materias.models import Materia, MateriaAsignada, ResultadoFinalMateria, TipoNota
from apps.materias.serializers import MateriaSerializer, MateriaAsignadaSerializer, ResultadoFinalMateriaSerializer, TipoNotaSerializer
from apps.evaluacion.models import Nota
from django.utils import timezone

class MateriaViewSet(viewsets.ModelViewSet):
    serializer_class = MateriaSerializer
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']

    def get_queryset(self):
        qs = Materia.objects.all()
        if getattr(self, 'action', None) == 'list':
            activo = self.request.query_params.get('activo')
            if activo is not None:
                qs = qs.filter(activo=(activo.lower() == 'true'))
            else:
                qs = qs.filter(activo=True)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        materia = self.get_object()
        materia.activo = True
        materia.save()
        return Response({'mensaje': 'Materia reactivada correctamente'})

class MateriaAsignadaViewSet(viewsets.ModelViewSet):
    queryset = MateriaAsignada.objects.all()
    serializer_class = MateriaAsignadaSerializer
    search_fields = ['ciclo', 'materia__nombre', 'maestro__persona__nombre', 'maestro__persona__apellido_paterno', 'seccion_grado__grado__nombre', 'seccion_grado__seccion__nombre']
    ordering_fields = ['ciclo', 'materia', 'maestro', 'seccion_grado']

    def get_queryset(self):
        qs = MateriaAsignada.objects.all()
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(ciclo__icontains=search) |
                Q(materia__nombre__icontains=search) |
                Q(maestro__persona__nombre__icontains=search) |
                Q(maestro__persona__apellido_paterno__icontains=search) |
                Q(seccion_grado__grado__nombre__icontains=search) |
                Q(seccion_grado__seccion__nombre__icontains=search)
            )
        return qs

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

    @action(detail=False, methods=['post'], url_path='calcular')
    def calcular_resultados(self, request):
        """
        Calcula y actualiza los resultados finales de materia para todos los alumnos de una materia_asignada y ciclo.
        Espera: { "materia_asignada": id, "ciclo": "2025" }
        """
        materia_asignada_id = request.data.get('materia_asignada')
        ciclo = request.data.get('ciclo')
        if not materia_asignada_id or not ciclo:
            return Response({'error': 'materia_asignada y ciclo son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            materia_asignada = MateriaAsignada.objects.get(id=materia_asignada_id)
        except MateriaAsignada.DoesNotExist:
            return Response({'error': 'Materia asignada no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        tipos_nota = TipoNota.objects.filter(materia_asignada=materia_asignada)
        if not tipos_nota.exists():
            return Response({'error': 'No hay tipos de nota definidos para esta materia asignada'}, status=status.HTTP_400_BAD_REQUEST)
        suma_pesos = sum(t.peso for t in tipos_nota)
        if suma_pesos == 0:
            return Response({'error': 'La suma de los pesos de los tipos de nota es 0'}, status=status.HTTP_400_BAD_REQUEST)
        # Alumnos inscritos en la sección de esta materia_asignada y ciclo
        seccion_grado = materia_asignada.seccion_grado
        from apps.secciones.models import SeccionAlumno
        inscripciones = SeccionAlumno.objects.filter(seccion_grado=seccion_grado, ciclo=ciclo, estado='activo')
        resultados = []
        for insc in inscripciones:
            alumno = insc.alumno
            total = 0
            for tipo in tipos_nota:
                nota = Nota.objects.filter(alumno=alumno, tipo_nota=tipo, materia_asignada=materia_asignada).first()
                valor = nota.calificacion if nota else 0
                total += (valor * tipo.peso / 100)
            promedio = round(total, 2)
            aprobado = promedio >= 51  # O el umbral que definas
            obj, _ = ResultadoFinalMateria.objects.update_or_create(
                alumno=alumno,
                materia_asignada=materia_asignada,
                ciclo=ciclo,
                defaults={
                    'promedio': promedio,
                    'aprobado': aprobado,
                    'fecha_cierre': timezone.now().date(),
                    'observacion': ''
                }
            )
            resultados.append({
                'alumno_id': alumno.id,
                'promedio': promedio,
                'aprobado': aprobado
            })
        return Response({'resultados': resultados, 'mensaje': f'Resultados calculados para {len(resultados)} alumnos.'})
