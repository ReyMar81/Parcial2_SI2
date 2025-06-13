from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from apps.materias.models import Materia, MateriaAsignada, ResultadoFinalMateria, TipoNota
from apps.materias.serializers import MateriaSerializer, MateriaAsignadaSerializer, ResultadoFinalMateriaSerializer, TipoNotaSerializer
from apps.evaluacion.models import Nota
from django.utils import timezone
from apps.secciones.models import SeccionAlumno
from apps.personas.serializers import AlumnoSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

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

    @extend_schema(
        parameters=[
            OpenApiParameter("maestro", OpenApiTypes.INT, OpenApiParameter.QUERY, required=True, description="ID del maestro"),
            OpenApiParameter("ciclo", OpenApiTypes.STR, OpenApiParameter.QUERY, required=False, description="Ciclo escolar (opcional)")
        ],
        responses={200: dict},
        description="Lista las materias asignadas a un maestro, incluyendo los alumnos de cada sección/grado y ciclo."
    )
    @action(detail=False, methods=["get"], url_path="por-maestro")
    def materias_asignadas_por_maestro(self, request):
        maestro_id = request.query_params.get("maestro")
        ciclo = request.query_params.get("ciclo")
        print(f"[LOG] maestro_id: {maestro_id}, ciclo: {ciclo}")
        qs = self.get_queryset().filter(maestro_id=maestro_id)
        if ciclo:
            qs = qs.filter(ciclo=ciclo)
        print(f"[LOG] queryset count: {qs.count()}")
        result = []
        for ma in qs:
            print(f"[LOG] MateriaAsignada: id={ma.id}, ciclo={ma.ciclo}, maestro_id={ma.maestro_id}")
            alumnos_qs = SeccionAlumno.objects.filter(
                seccion_grado=ma.seccion_grado,
                ciclo=ma.ciclo,
                estado='activo'
            )
            print(f"[LOG] Alumnos count for materia_asignada {ma.id}: {alumnos_qs.count()}")
            alumnos = [AlumnoSerializer(sa.alumno).data for sa in alumnos_qs]
            ma_data = self.get_serializer(ma).data
            ma_data["alumnos"] = alumnos
            result.append(ma_data)
        return Response(result)

    @extend_schema(
        parameters=[
            OpenApiParameter("maestro", OpenApiTypes.INT, OpenApiParameter.QUERY, required=True, description="ID del maestro"),
            OpenApiParameter("ciclo", OpenApiTypes.STR, OpenApiParameter.QUERY, required=False, description="Ciclo escolar (opcional)")
        ],
        responses={200: dict},
        description="Lista solo las materias asignadas a un maestro y ciclo, sin incluir alumnos. Respuesta ligera para apps móviles."
    )
    @action(detail=False, methods=["get"], url_path="por-maestro-simple")
    def materias_asignadas_por_maestro_simple(self, request):
        maestro_id = request.query_params.get("maestro")
        ciclo = request.query_params.get("ciclo")
        qs = self.get_queryset().filter(maestro_id=maestro_id)
        if ciclo:
            qs = qs.filter(ciclo=ciclo)
        result = []
        for ma in qs:
            result.append({
                "id": ma.id,
                "ciclo": ma.ciclo,
                "materia": {"id": ma.materia.id, "nombre": ma.materia.nombre},
                "seccion_grado": {
                    "id": ma.seccion_grado.id,
                    "nombre": str(ma.seccion_grado)
                }
            })
        return Response(result)

    @extend_schema(
        parameters=[
            OpenApiParameter("materia_asignada", OpenApiTypes.INT, OpenApiParameter.QUERY, required=True, description="ID de la materia_asignada")
        ],
        responses={200: dict},
        description="Lista los alumnos activos de una materia_asignada específica y ciclo."
    )
    @action(detail=False, methods=["get"], url_path="alumnos-por-materia-asignada")
    def alumnos_por_materia_asignada(self, request):
        materia_asignada_id = request.query_params.get("materia_asignada")
        if not materia_asignada_id:
            return Response({'error': 'Debe proporcionar el id de materia_asignada'}, status=400)
        try:
            ma = MateriaAsignada.objects.get(id=materia_asignada_id)
        except MateriaAsignada.DoesNotExist:
            return Response({'error': 'Materia asignada no encontrada'}, status=404)
        ciclo = ma.ciclo
        alumnos_qs = SeccionAlumno.objects.filter(
            seccion_grado=ma.seccion_grado,
            ciclo=ciclo,
            estado='activo'
        )
        alumnos = [AlumnoSerializer(sa.alumno).data for sa in alumnos_qs]
        return Response(alumnos)

    @extend_schema(
        parameters=[
            OpenApiParameter("alumno", OpenApiTypes.INT, OpenApiParameter.QUERY, required=True, description="ID del alumno"),
            OpenApiParameter("ciclo", OpenApiTypes.STR, OpenApiParameter.QUERY, required=False, description="Ciclo escolar (opcional)")
        ],
        responses={200: dict},
        description="Lista las materias asignadas a un alumno, filtrando por ciclo si se provee. Respuesta ligera para apps móviles."
    )
    @action(detail=False, methods=["get"], url_path="por-alumno")
    def materias_asignadas_por_alumno(self, request):
        alumno_id = request.query_params.get("alumno")
        ciclo = request.query_params.get("ciclo")
        if not alumno_id:
            return Response({'error': 'Debe proporcionar el id de alumno'}, status=400)
        from apps.secciones.models import SeccionAlumno
        seccion_alumnos = SeccionAlumno.objects.filter(alumno_id=alumno_id, estado='activo')
        if ciclo:
            seccion_alumnos = seccion_alumnos.filter(ciclo=ciclo)
        seccion_grado_ids = seccion_alumnos.values_list('seccion_grado_id', flat=True)
        qs = self.get_queryset().filter(seccion_grado_id__in=seccion_grado_ids)
        if ciclo:
            qs = qs.filter(ciclo=ciclo)
        qs = qs.distinct()
        result = []
        for ma in qs:
            result.append({
                "id": ma.id,
                "ciclo": ma.ciclo,
                "materia": {"id": ma.materia.id, "nombre": ma.materia.nombre},
                "seccion_grado": {
                    "id": ma.seccion_grado.id,
                    "nombre": str(ma.seccion_grado)
                }
            })
        return Response(result)

class TipoNotaViewSet(viewsets.ModelViewSet):
    queryset = TipoNota.objects.all()
    serializer_class = TipoNotaSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="materia_asignada",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID de la materia_asignada para filtrar los tipos de nota"
            )
        ],
        responses={200: TipoNotaSerializer(many=True)},
        description="Devuelve los tipos de nota asociados a un id de materia_asignada."
    )
    @action(detail=False, methods=['get'], url_path='por-materia-asignada')
    def por_materia_asignada(self, request):
        """
        Devuelve los tipos de nota asociados a un id de materia_asignada.
        GET param: materia_asignada=<id>
        """
        materia_asignada_id = request.query_params.get('materia_asignada')
        if not materia_asignada_id:
            return Response({'error': 'Debe proporcionar el id de materia_asignada'}, status=400)
        tipos = TipoNota.objects.filter(materia_asignada=materia_asignada_id)
        data = self.get_serializer(tipos, many=True).data
        return Response(data)

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
