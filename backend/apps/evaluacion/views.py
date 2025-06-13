from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from datetime import date
from apps.evaluacion.models import Nota, Asistencia, Participacion
from apps.evaluacion.serializers import NotaSerializer, AsistenciaSerializer, ParticipacionSerializer
from rest_framework.views import APIView
import joblib
import numpy as np
from rest_framework.permissions import AllowAny
from django.db.models import Avg
from apps.personas.models import FCMToken
import requests
from django.conf import settings
from apps.personas.services import send_fcm_v1_notification

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
        description="Permite crear o actualizar muchas notas en una sola petición (upsert). Espera un array de objetos con los campos: alumno, tipo_nota, materia_asignada, calificacion. La fecha se asigna automáticamente si no se envía. Se recomienda enviar solo las notas de un tipo de nota por petición para eficiencia."
    )
    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk_create(self, request):
        """
        Permite crear o actualizar muchas notas en una sola petición (upsert).
        Espera un array de objetos con los campos: alumno, tipo_nota, materia_asignada, calificacion.
        Puede enviar notas de diferentes tipos y materias.
        """
        notas_data = request.data
        if not isinstance(notas_data, list) or not notas_data:
            return Response({'error': 'Se espera una lista de notas no vacía.'}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        errors = []
        for idx, nota in enumerate(notas_data):
            # Validar campos mínimos
            required_fields = ['alumno', 'tipo_nota', 'materia_asignada', 'calificacion']
            if not all(field in nota for field in required_fields):
                errors.append({'index': idx, 'errors': f'Faltan campos requeridos: {required_fields}'})
                continue
            if 'fecha' not in nota or not nota['fecha']:
                nota['fecha'] = date.today()
            obj = Nota.objects.filter(alumno=nota['alumno'], tipo_nota=nota['tipo_nota'], materia_asignada=nota['materia_asignada']).first()
            serializer = NotaSerializer(obj, data=nota)
            if serializer.is_valid():
                nota_obj = serializer.save()
                results.append(serializer.data)
                # --- Notificación push FCM v1 ---
                try:
                    from apps.personas.models import Alumno, Persona
                    from apps.materias.models import MateriaAsignada, TipoNota
                    alumno_obj = Alumno.objects.get(id=nota['alumno'])
                    persona = alumno_obj.persona
                    user = persona.usuario
                    materia_asignada = MateriaAsignada.objects.get(id=nota['materia_asignada'])
                    materia_nombre = materia_asignada.materia.nombre
                    maestro_nombre = materia_asignada.maestro.persona.nombre + ' ' + materia_asignada.maestro.persona.apellido_paterno
                    tipo_nota = TipoNota.objects.get(id=nota['tipo_nota'])
                    tipo_nota_nombre = tipo_nota.nombre
                    tokens = FCMToken.objects.filter(user=user)
                    for t in tokens:
                        send_fcm_v1_notification(
                            t.token,
                            title="Nueva nota registrada",
                            body=f"Materia: {materia_nombre} | Nota: {nota['calificacion']} | Tipo: {tipo_nota_nombre} | Maestro: {maestro_nombre}",
                            data={
                                "materia_id": str(materia_asignada.materia.id),
                                "materia_nombre": materia_nombre,
                                "nota_id": str(nota_obj.id),
                                "calificacion": str(nota['calificacion']),
                                "maestro": maestro_nombre,
                                "tipo": "nota",
                                "tipo_nota": tipo_nota_nombre
                            }
                        )
                except Exception as e:
                    print(f"[FCM ERROR bulk_create]: {e}")
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
                description="ID de la materia_asignada para filtrar las notas"
            ),
            OpenApiParameter(
                name="tipo_nota",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID del tipo de nota para filtrar las notas"
            )
        ],
        responses={200: NotaSerializer(many=True)},
        description="Lista las notas de los alumnos para una materia_asignada y tipo_nota específicos. Respuesta ligera para apps móviles."
    )
    @action(detail=False, methods=["get"], url_path="por-materia-y-tipo-nota")
    def notas_por_materia_y_tipo_nota(self, request):
        import logging
        logger = logging.getLogger("evaluacion.notas_por_materia_y_tipo_nota")
        materia_asignada_id = request.query_params.get('materia_asignada')
        tipo_nota_id = request.query_params.get('tipo_nota')
        logger.info(f"[API] Notas por materia y tipo: materia_asignada={materia_asignada_id}, tipo_nota={tipo_nota_id}")
        if not materia_asignada_id or not tipo_nota_id:
            logger.warning("Faltan parámetros obligatorios.")
            return Response({'error': 'Debe proporcionar materia_asignada y tipo_nota'}, status=400)
        try:
            queryset = self.get_queryset().filter(materia_asignada=materia_asignada_id, tipo_nota=tipo_nota_id)
            logger.info(f"[API] Queryset count: {queryset.count()}")
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"[API] Serialización exitosa. Respuesta de longitud: {len(serializer.data)}")
            return Response(serializer.data)
        except Exception as e:
            import traceback
            logger.error(f"[API][ERROR] {e}")
            logger.error(traceback.format_exc())
            return Response({'error': f'Error interno: {str(e)}'}, status=500)

    @extend_schema(
        request=NotaSerializer(many=True),
        responses={201: NotaSerializer(many=True)},
        description="[APP MÓVIL] Permite crear o actualizar muchas notas de un solo tipo de nota y materia_asignada en una sola petición (upsert liviano). Espera un array de objetos con los campos: alumno, tipo_nota, materia_asignada, calificacion. La fecha se asigna automáticamente si no se envía. Solo acepta un tipo_nota y materia_asignada por petición."
    )
    @action(detail=False, methods=['post'], url_path='bulk-mobile')
    def bulk_create_mobile(self, request):
        """
        [APP MÓVIL] Permite crear o actualizar muchas notas de un solo tipo de nota y materia_asignada en una sola petición (upsert liviano).
        Espera un array de objetos con los campos: alumno, tipo_nota, materia_asignada, calificacion.
        Solo se permite un tipo_nota y materia_asignada por petición para minimizar la carga y evitar errores.
        """
        notas_data = request.data
        if not isinstance(notas_data, list) or not notas_data:
            return Response({'error': 'Se espera una lista de notas no vacía.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que todas las notas sean del mismo tipo_nota y materia_asignada
        tipo_nota_set = set(n['tipo_nota'] for n in notas_data)
        materia_asignada_set = set(n['materia_asignada'] for n in notas_data)
        if len(tipo_nota_set) != 1 or len(materia_asignada_set) != 1:
            return Response({'error': 'Todas las notas deben ser del mismo tipo_nota y materia_asignada.'}, status=status.HTTP_400_BAD_REQUEST)

        tipo_nota_id = list(tipo_nota_set)[0]
        materia_asignada_id = list(materia_asignada_set)[0]

        results = []
        errors = []
        for idx, nota in enumerate(notas_data):
            if 'fecha' not in nota or not nota['fecha']:
                nota['fecha'] = date.today()
            obj = Nota.objects.filter(alumno=nota['alumno'], tipo_nota=tipo_nota_id, materia_asignada=materia_asignada_id).first()
            serializer = NotaSerializer(obj, data=nota)
            if serializer.is_valid():
                nota_obj = serializer.save()
                results.append(serializer.data)
                try:
                    from apps.personas.models import Alumno, Persona
                    from apps.materias.models import MateriaAsignada, TipoNota
                    alumno_obj = Alumno.objects.get(id=nota['alumno'])
                    persona = alumno_obj.persona
                    user = persona.usuario
                    materia_asignada = MateriaAsignada.objects.get(id=materia_asignada_id)
                    materia_nombre = materia_asignada.materia.nombre
                    maestro_nombre = materia_asignada.maestro.persona.nombre + ' ' + materia_asignada.maestro.persona.apellido_paterno
                    tipo_nota = TipoNota.objects.get(id=tipo_nota_id)
                    tipo_nota_nombre = tipo_nota.nombre
                    tokens = FCMToken.objects.filter(user=user)
                    for t in tokens:
                        send_fcm_v1_notification(
                            t.token,
                            title="Nueva nota registrada",
                            body=f"Materia: {materia_nombre} | Nota: {nota['calificacion']} | Tipo: {tipo_nota_nombre} | Maestro: {maestro_nombre}",
                            data={
                                "materia_id": str(materia_asignada.materia.id),
                                "materia_nombre": materia_nombre,
                                "nota_id": str(nota_obj.id),
                                "calificacion": str(nota['calificacion']),
                                "maestro": maestro_nombre,
                                "tipo": "nota",
                                "tipo_nota": tipo_nota_nombre
                            }
                        )
                except Exception as e:
                    print(f"[FCM ERROR bulk_create_mobile]: {e}")
            else:
                errors.append({'index': idx, 'errors': serializer.errors})
        if errors:
            return Response({'results': results, 'errors': errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response(results, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="alumno",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID del alumno"
            ),
            OpenApiParameter(
                name="materia_asignada",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID de la materia_asignada"
            )
        ],
        responses={200: NotaSerializer(many=True)},
        description="Lista todas las notas de un alumno para una materia_asignada."
    )
    @action(detail=False, methods=["get"], url_path="por-alumno-y-materia")
    def notas_por_alumno_y_materia(self, request):
        alumno_id = request.query_params.get('alumno')
        materia_asignada_id = request.query_params.get('materia_asignada')
        if not alumno_id or not materia_asignada_id:
            return Response({'error': 'Debe proporcionar alumno y materia_asignada.'}, status=400)
        queryset = self.get_queryset().filter(alumno=alumno_id, materia_asignada=materia_asignada_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="materia_asignada",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID de la materia_asignada para filtrar las asistencias"
            )
        ],
        responses={200: AsistenciaSerializer(many=True)},
        description="Lista todas las asistencias de los alumnos para una materia_asignada (sin filtrar por fecha)."
    )
    @action(detail=False, methods=["get"], url_path="por-materia")
    def get_asistencias_por_materia(self, request):
        materia_asignada_id = request.query_params.get('materia_asignada')
        if not materia_asignada_id:
            return Response({'error': 'Debe proporcionar materia_asignada.'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(materia_asignada=materia_asignada_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="alumno",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID del alumno"
            ),
            OpenApiParameter(
                name="materia_asignada",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID de la materia_asignada"
            )
        ],
        responses={200: AsistenciaSerializer(many=True)},
        description="Lista todas las asistencias de un alumno para una materia_asignada."
    )
    @action(detail=False, methods=["get"], url_path="por-alumno-y-materia")
    def asistencias_por_alumno_y_materia(self, request):
        alumno_id = request.query_params.get('alumno')
        materia_asignada_id = request.query_params.get('materia_asignada')
        if not alumno_id or not materia_asignada_id:
            return Response({'error': 'Debe proporcionar alumno y materia_asignada.'}, status=400)
        queryset = self.get_queryset().filter(alumno=alumno_id, materia_asignada=materia_asignada_id)
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="materia_asignada",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID de la materia_asignada para filtrar las participaciones"
            )
        ],
        responses={200: ParticipacionSerializer(many=True)},
        description="Lista todas las participaciones de los alumnos para una materia_asignada (sin filtrar por fecha)."
    )
    @action(detail=False, methods=["get"], url_path="por-materia")
    def get_participaciones_por_materia(self, request):
        materia_asignada_id = request.query_params.get('materia_asignada')
        if not materia_asignada_id:
            return Response({'error': 'Debe proporcionar materia_asignada.'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(materia_asignada=materia_asignada_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="alumno",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID del alumno"
            ),
            OpenApiParameter(
                name="materia_asignada",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID de la materia_asignada"
            )
        ],
        responses={200: ParticipacionSerializer(many=True)},
        description="Lista todas las participaciones de un alumno para una materia_asignada."
    )
    @action(detail=False, methods=["get"], url_path="por-alumno-y-materia")
    def participaciones_por_alumno_y_materia(self, request):
        alumno_id = request.query_params.get('alumno')
        materia_asignada_id = request.query_params.get('materia_asignada')
        if not alumno_id or not materia_asignada_id:
            return Response({'error': 'Debe proporcionar alumno y materia_asignada.'}, status=400)
        queryset = self.get_queryset().filter(alumno=alumno_id, materia_asignada=materia_asignada_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# --- Función para enviar notificación FCM ---
def send_fcm_notification(token, title, body):
    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {
        'Authorization': f'key={getattr(settings, "FCM_SERVER_KEY", "TU_SERVER_KEY_AQUI")}',
        'Content-Type': 'application/json'
    }
    payload = {
        'to': token,
        'notification': {
            'title': title,
            'body': body,
            'sound': 'default'
        },
        'data': {
            'click_action': 'FLUTTER_NOTIFICATION_CLICK',
            'id': '1',
            'status': 'done'
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()