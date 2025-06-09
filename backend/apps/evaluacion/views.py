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

class ParticipacionViewSet(viewsets.ModelViewSet):
    queryset = Participacion.objects.all()
    serializer_class = ParticipacionSerializer