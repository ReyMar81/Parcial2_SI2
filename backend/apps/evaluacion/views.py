from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from datetime import date
from apps.evaluacion.models import Nota, Asistencia, Participacion
from apps.evaluacion.serializers import NotaSerializer, AsistenciaSerializer, ParticipacionSerializer

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="materia_asignada",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="ID de la materia_asignada para filtrar las notas"
            )
        ],
        responses={200: NotaSerializer(many=True)},
        description="Lista todas las notas, permite filtrar por materia_asignada."
    )
    def list(self, request, *args, **kwargs):
        materia_asignada_id = request.query_params.get('materia_asignada')
        queryset = self.get_queryset()
        if materia_asignada_id:
            queryset = queryset.filter(materia_asignada=materia_asignada_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=NotaSerializer(many=True),
        responses={201: NotaSerializer(many=True)},
        description="Permite crear o actualizar muchas notas en una sola petición (upsert). Espera un array de objetos con los campos: alumno, tipo_nota, materia_asignada, calificacion. La fecha se asigna automáticamente si no se envía."
    )
    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk_create(self, request):
        """
        Permite crear o actualizar muchas notas en una sola petición (upsert).
        Espera un array de objetos con los campos: alumno, tipo_nota, materia_asignada, calificacion.
        """
        notas_data = request.data
        if not isinstance(notas_data, list):
            return Response({'error': 'Se espera una lista de notas.'}, status=status.HTTP_400_BAD_REQUEST)
        results = []
        errors = []
        for idx, nota in enumerate(notas_data):
            if 'fecha' not in nota or not nota['fecha']:
                nota['fecha'] = date.today()
            # Buscar si ya existe la nota (alumno + tipo_nota)
            obj = Nota.objects.filter(alumno=nota['alumno'], tipo_nota=nota['tipo_nota']).first()
            serializer = NotaSerializer(obj, data=nota)
            if serializer.is_valid():
                serializer.save()
                results.append(serializer.data)
            else:
                errors.append({'index': idx, 'errors': serializer.errors})
        if errors:
            return Response({'results': results, 'errors': errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response(results, status=status.HTTP_201_CREATED)

class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer

    @extend_schema(
        request=AsistenciaSerializer(many=True),
        responses={201: AsistenciaSerializer(many=True)},
        description="Permite crear o actualizar muchas asistencias en una sola petición (upsert). Espera un array de objetos con los campos: alumno, materia_asignada, fecha, estado. Si ya existe para ese alumno, materia y fecha, actualiza el estado."
    )
    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk_create(self, request):
        asistencias_data = request.data
        if not isinstance(asistencias_data, list):
            return Response({'error': 'Se espera una lista de asistencias.'}, status=status.HTTP_400_BAD_REQUEST)
        results = []
        errors = []
        for idx, asistencia in enumerate(asistencias_data):
            if 'fecha' not in asistencia or not asistencia['fecha']:
                asistencia['fecha'] = date.today()
            # Buscar si ya existe la asistencia (alumno + materia_asignada + fecha)
            obj = Asistencia.objects.filter(
                alumno=asistencia['alumno'],
                materia_asignada=asistencia['materia_asignada'],
                fecha=asistencia['fecha']
            ).first()
            serializer = AsistenciaSerializer(obj, data=asistencia)
            if serializer.is_valid():
                serializer.save()
                results.append(serializer.data)
            else:
                errors.append({'index': idx, 'errors': serializer.errors})
        if errors:
            return Response({'results': results, 'errors': errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response(results, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="materia_asignada",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID de la materia_asignada para filtrar las asistencias"
            ),
            OpenApiParameter(
                name="fecha",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Fecha de la asistencia en formato YYYY-MM-DD"
            )
        ],
        responses={200: AsistenciaSerializer(many=True)},
        description="Lista las asistencias de los alumnos para una materia_asignada y fecha específica."
    )
    @action(detail=False, methods=["get"], url_path="por-materia-y-fecha")
    def get_asistencias_por_materia_y_fecha(self, request):
        materia_asignada_id = request.query_params.get('materia_asignada')
        fecha = request.query_params.get('fecha')
        if not materia_asignada_id or not fecha:
            return Response({'error': 'Debe proporcionar materia_asignada y fecha.'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(materia_asignada=materia_asignada_id, fecha=fecha)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ParticipacionViewSet(viewsets.ModelViewSet):
    queryset = Participacion.objects.all()
    serializer_class = ParticipacionSerializer

    @extend_schema(
        request=ParticipacionSerializer(many=True),
        responses={201: ParticipacionSerializer(many=True)},
        description="Permite crear o actualizar muchas participaciones en una sola petición (upsert). Espera un array de objetos con los campos: alumno, materia_asignada, fecha, puntaje, observacion. Si ya existe para ese alumno, materia y fecha, actualiza el puntaje y observacion."
    )
    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk_create(self, request):
        participaciones_data = request.data
        if not isinstance(participaciones_data, list):
            return Response({'error': 'Se espera una lista de participaciones.'}, status=status.HTTP_400_BAD_REQUEST)
        results = []
        errors = []
        for idx, participacion in enumerate(participaciones_data):
            if 'fecha' not in participacion or not participacion['fecha']:
                participacion['fecha'] = date.today()
            # Buscar si ya existe la participacion (alumno + materia_asignada + fecha)
            obj = Participacion.objects.filter(
                alumno=participacion['alumno'],
                materia_asignada=participacion['materia_asignada'],
                fecha=participacion['fecha']
            ).first()
            serializer = ParticipacionSerializer(obj, data=participacion)
            if serializer.is_valid():
                serializer.save()
                results.append(serializer.data)
            else:
                errors.append({'index': idx, 'errors': serializer.errors})
        if errors:
            return Response({'results': results, 'errors': errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response(results, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="materia_asignada",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID de la materia_asignada para filtrar las participaciones"
            ),
            OpenApiParameter(
                name="fecha",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Fecha de la participación en formato YYYY-MM-DD"
            )
        ],
        responses={200: ParticipacionSerializer(many=True)},
        description="Lista las participaciones de los alumnos para una materia_asignada y fecha específica."
    )
    @action(detail=False, methods=["get"], url_path="por-materia-y-fecha")
    def get_participaciones_por_materia_y_fecha(self, request):
        materia_asignada_id = request.query_params.get('materia_asignada')
        fecha = request.query_params.get('fecha')
        if not materia_asignada_id or not fecha:
            return Response({'error': 'Debe proporcionar materia_asignada y fecha.'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(materia_asignada=materia_asignada_id, fecha=fecha)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)