from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.secciones.models import Grado, Seccion, SeccionGrado, SeccionAlumno, ResultadoFinalSeccion
from apps.secciones.serializers import GradoSerializer, SeccionSerializer, SeccionGradoSerializer, SeccionAlumnoSerializer, ResultadoFinalSeccionSerializer
from django.shortcuts import get_object_or_404
from apps.materias.models import MateriaAsignada, ResultadoFinalMateria
from django.utils import timezone

class GradoViewSet(viewsets.ModelViewSet):
    serializer_class = GradoSerializer
    search_fields = ['nombre', 'nivel']
    ordering_fields = ['nombre', 'nivel']

    def get_queryset(self):
        # Permitir buscar por todos los grados si se pasa un parámetro especial
        all_param = self.request.query_params.get('all')
        if all_param == 'true':
            return Grado.objects.all()
        # Solo mostrar grados activos por defecto
        qs = Grado.objects.filter(activo=True)
        activo = self.request.query_params.get('activo')
        if activo is not None:
            qs = Grado.objects.filter(activo=(activo.lower() == 'true'))
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activo = False
        instance.save()
        SeccionGrado.objects.filter(grado=instance).update(activo=False)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        # PUT/PATCH: solo permite edición si está activo
        instance = self.get_object()
        if not instance.activo:
            return Response({'error': 'No se puede editar un grado inactivo.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        # Buscar el grado aunque esté inactivo
        try:
            grado = Grado.objects.get(pk=pk)
        except Grado.DoesNotExist:
            return Response({'error': 'Grado no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        grado.activo = True
        grado.save()
        # Reactivar solo relaciones donde la sección también está activa
        SeccionGrado.objects.filter(grado=grado, seccion__activo=True).update(activo=True)
        return Response({'mensaje': 'Grado y relaciones reactivados correctamente'})

class SeccionViewSet(viewsets.ModelViewSet):
    serializer_class = SeccionSerializer
    search_fields = ['nombre']
    ordering_fields = ['nombre']

    def get_queryset(self):
        # Solo mostrar secciones activas por defecto
        qs = Seccion.objects.filter(activo=True)
        activo = self.request.query_params.get('activo')
        if activo is not None:
            qs = Seccion.objects.filter(activo=(activo.lower() == 'true'))
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activo = False
        instance.save()
        SeccionGrado.objects.filter(seccion=instance).update(activo=False)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        # PUT/PATCH: solo permite edición si está activa
        instance = self.get_object()
        if not instance.activo:
            return Response({'error': 'No se puede editar una sección inactiva.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        # Buscar la sección aunque esté inactiva
        try:
            seccion = Seccion.objects.get(pk=pk)
        except Seccion.DoesNotExist:
            return Response({'error': 'Sección no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        seccion.activo = True
        seccion.save()
        # Reactivar solo relaciones donde el grado también está activo
        SeccionGrado.objects.filter(seccion=seccion, grado__activo=True).update(activo=True)
        return Response({'mensaje': 'Sección y relaciones reactivadas correctamente'})

class SeccionGradoViewSet(viewsets.ModelViewSet):
    queryset = SeccionGrado.objects.filter(activo=True)
    serializer_class = SeccionGradoSerializer
    search_fields = ['aula', 'seccion__nombre', 'grado__nombre']
    ordering_fields = ['aula', 'capacidad_maxima']

    def get_queryset(self):
        # Solo mostrar relaciones activas por defecto
        qs = SeccionGrado.objects.filter(activo=True)
        activo = self.request.query_params.get('activo')
        if activo is not None:
            qs = SeccionGrado.objects.filter(activo=(activo.lower() == 'true'))
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        # PUT/PATCH: solo permite edición si está activa
        instance = self.get_object()
        if not instance.activo:
            return Response({'error': 'No se puede editar una relación inactiva.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        # Buscar la relación aunque esté inactiva
        seccion_grado = get_object_or_404(SeccionGrado, pk=pk)
        # Solo reactiva si ambos están activos
        if seccion_grado.seccion.activo and seccion_grado.grado.activo:
            seccion_grado.activo = True
            seccion_grado.save()
            return Response({'mensaje': 'Sección-Grado reactivada correctamente'})
        return Response({'error': 'No se puede reactivar la relación si grado o sección están inactivos.'}, status=status.HTTP_400_BAD_REQUEST)

class SeccionAlumnoViewSet(viewsets.ModelViewSet):
    queryset = SeccionAlumno.objects.all()
    serializer_class = SeccionAlumnoSerializer

class ResultadoFinalSeccionViewSet(viewsets.ModelViewSet):
    queryset = ResultadoFinalSeccion.objects.all()
    serializer_class = ResultadoFinalSeccionSerializer

    @action(detail=False, methods=['post'], url_path='calcular')
    def calcular_resultados(self, request):
        """
        Calcula y actualiza los resultados finales de sección para todos los alumnos de una sección_grado y ciclo.
        Espera: { "seccion_grado": id, "ciclo": "2025" }
        """
        seccion_grado_id = request.data.get('seccion_grado')
        ciclo = request.data.get('ciclo')
        if not seccion_grado_id or not ciclo:
            return Response({'error': 'seccion_grado y ciclo son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        from apps.secciones.models import SeccionAlumno
        inscripciones = SeccionAlumno.objects.filter(seccion_grado=seccion_grado_id, ciclo=ciclo, estado='activo')
        resultados = []
        for insc in inscripciones:
            alumno = insc.alumno
            # Busca todas las materias asignadas a la sección y ciclo
            materias_asignadas = MateriaAsignada.objects.filter(seccion_grado=seccion_grado_id, ciclo=ciclo)
            # Busca los resultados finales de esas materias
            resultados_materia = ResultadoFinalMateria.objects.filter(alumno=alumno, materia_asignada__in=materias_asignadas, ciclo=ciclo)
            total_materias = materias_asignadas.count()
            materias_aprobadas = resultados_materia.filter(aprobado=True).count()
            aprobado = (total_materias > 0 and materias_aprobadas == total_materias)
            obj, _ = ResultadoFinalSeccion.objects.update_or_create(
                seccion_alumno=insc,
                ciclo=ciclo,
                defaults={
                    'aprobado': aprobado,
                    'fecha_cierre': timezone.now().date()
                }
            )
            resultados.append({
                'alumno_id': alumno.id,
                'aprobado': aprobado
            })
        return Response({'resultados': resultados, 'mensaje': f'Resultados calculados para {len(resultados)} alumnos.'})