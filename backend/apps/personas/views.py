from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from apps.personas.models import Persona, Alumno, Maestro, Tutor, TutorAlumno
from apps.personas.serializers import PersonaSerializer, AlumnoSerializer, MaestroSerializer, TutorSerializer, TutorAlumnoSerializer, InscripcionSerializer, ActualizarAlumnosTutorSerializer
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.personas.services import crear_usuario_persona_rol, send_fcm_v1_notification
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.secciones.models import Seccion, SeccionAlumno
from datetime import date
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import FCMToken

class PersonaViewSet(viewsets.ModelViewSet):
    serializer_class = PersonaSerializer
    def get_queryset(self):
        return Persona.objects.filter(activo=True)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activo = False
        instance.save()
        if instance.usuario:
            instance.usuario.is_active = False
            instance.usuario.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AlumnoViewSet(viewsets.ModelViewSet):
    serializer_class = AlumnoSerializer
    search_fields = ['persona__nombre', 'persona__apellido_paterno', 'persona__apellido_materno', 'persona__ci', 'registro']
    ordering_fields = ['persona__nombre', 'registro']
    def get_queryset(self):
        qs = Alumno.objects.all()
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
        # Desactivar la persona asociada
        if instance.persona:
            instance.persona.activo = False
            instance.persona.save()
            # Desactivar el usuario asociado
            if instance.persona.usuario:
                instance.persona.usuario.is_active = False
                instance.persona.usuario.save()
        # Desactivar relaciones TutorAlumno
        TutorAlumno.objects.filter(alumno=instance, activo=True).update(activo=False)
        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        alumno = self.get_object()
        alumno.activo = True
        alumno.save()
        if alumno.persona:
            alumno.persona.activo = True
            alumno.persona.save()
            if alumno.persona.usuario:
                alumno.persona.usuario.is_active = True
                alumno.persona.usuario.save()
        # Reactivar relaciones TutorAlumno si el tutor está activo
        from apps.personas.models import TutorAlumno
        TutorAlumno.objects.filter(alumno=alumno, activo=False, tutor__activo=True).update(activo=True)
        return Response({'mensaje': 'Alumno reactivado correctamente'})

class MaestroViewSet(viewsets.ModelViewSet):
    serializer_class = MaestroSerializer
    search_fields = ['persona__nombre', 'persona__apellido_paterno', 'persona__apellido_materno', 'persona__ci', 'registro']
    ordering_fields = ['persona__nombre', 'registro']
    def get_queryset(self):
        qs = Maestro.objects.all()
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
        if instance.persona:
            instance.persona.activo = False
            instance.persona.save()
            if instance.persona.usuario:
                instance.persona.usuario.is_active = False
                instance.persona.usuario.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        maestro = serializer.save()
        # Custom response with credentials
        resp = {
            "mensaje": "Maestro registrado exitosamente",
            "maestro": {
                "registro": maestro.registro,
                "username": maestro.persona.usuario.username,
                "password": maestro.persona.ci
            }
        }
        return Response(resp, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        maestro = self.get_object()
        maestro.activo = True
        maestro.save()
        if maestro.persona:
            maestro.persona.activo = True
            maestro.persona.save()
            if maestro.persona.usuario:
                maestro.persona.usuario.is_active = True
                maestro.persona.usuario.save()
        return Response({'mensaje': 'Maestro reactivado correctamente'})

class TutorViewSet(viewsets.ModelViewSet):
    serializer_class = TutorSerializer
    search_fields = ['persona__nombre', 'persona__apellido_paterno', 'persona__apellido_materno', 'persona__ci']
    ordering_fields = ['persona__nombre']
    def get_queryset(self):
        qs = Tutor.objects.all()
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
        if instance.persona:
            instance.persona.activo = False
            instance.persona.save()
            if instance.persona.usuario:
                instance.persona.usuario.is_active = False
                instance.persona.usuario.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tutor = serializer.save()
        # Custom response with credentials
        resp = {
            "mensaje": "Tutor registrado exitosamente",
            "tutor": {
                "username": tutor.persona.usuario.username,
                "password": tutor.persona.ci
            }
        }
        return Response(resp, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['post'], url_path='reactivar')
    def reactivar(self, request, pk=None):
        tutor = self.get_object()
        tutor.activo = True
        tutor.save()
        if tutor.persona:
            tutor.persona.activo = True
            tutor.persona.save()
            if tutor.persona.usuario:
                tutor.persona.usuario.is_active = True
                tutor.persona.usuario.save()
        return Response({'mensaje': 'Tutor reactivado correctamente'})
    @extend_schema(
        request=ActualizarAlumnosTutorSerializer,
        responses={200: serializers.Serializer()}
    )
    @action(detail=True, methods=['post'], url_path='actualizar_alumnos')
    def actualizar_alumnos(self, request, pk=None):
        """
        Permite actualizar la lista de alumnos asociados a un tutor (agregar y quitar relaciones en lote).
        Recibe: { alumnos_ids: [1,2,3] }
        """
        tutor = self.get_object()
        alumnos_ids = request.data.get('alumnos_ids', [])
        from apps.personas.models import Alumno, TutorAlumno
        # Eliminar relaciones actuales no incluidas (desactivar en vez de borrar)
        TutorAlumno.objects.filter(tutor=tutor).exclude(alumno_id__in=alumnos_ids).update(activo=False)
        # Agregar nuevas relaciones o reactivar si ya existe
        for alumno_id in alumnos_ids:
            ta, created = TutorAlumno.objects.get_or_create(tutor=tutor, alumno_id=alumno_id)
            if not ta.activo:
                ta.activo = True
                ta.save()
        return Response({'mensaje': 'Alumnos asociados actualizados correctamente'})

class TutorAlumnoViewSet(viewsets.ModelViewSet):
    queryset = TutorAlumno.objects.all()
    serializer_class = TutorAlumnoSerializer

@extend_schema(
    request=InscripcionSerializer,
    responses={201: None}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inscripcion(request):
    alumno_data = request.data.get('alumno')
    tutor_data = request.data.get('tutor')
    tutor_existente_ci = request.data.get('tutor_existente_ci')
    tipo_relacion = request.data.get('tipo_relacion', '')
    seccion_grado_id = request.data.get('seccion_grado_id')
    ciclo = request.data.get('ciclo')

    # Validaciones mínimas
    if not alumno_data or not seccion_grado_id or not ciclo:
        return Response({'error': 'Datos de alumno, sección-grado y ciclo son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    from apps.personas.models import Persona, Tutor, TutorAlumno, Alumno
    # Buscar o crear alumno por CI
    alumno_persona = Persona.objects.filter(ci=alumno_data['ci']).first()
    if alumno_persona:
        # Si existe, debe ser un alumno
        try:
            alumno_obj = Alumno.objects.get(persona=alumno_persona)
        except Alumno.DoesNotExist:
            return Response({'error': 'El CI ya existe pero no corresponde a un alumno'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        alumno_obj = crear_usuario_persona_rol(alumno_data, rol='alumno')

    # Lógica para tutor existente o nuevo
    if tutor_existente_ci:
        try:
            tutor_obj = Tutor.objects.get(persona__ci=tutor_existente_ci)
        except Tutor.DoesNotExist:
            return Response({'error': 'El tutor con ese CI no existe'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if not tutor_data:
            return Response({'error': 'Datos del tutor requeridos si no se usa tutor existente'}, status=status.HTTP_400_BAD_REQUEST)
        # No permitir duplicado de tutor
        if Persona.objects.filter(ci=tutor_data['ci']).exists():
            return Response({'error': 'El tutor ya tiene un usuario, use el campo tutor_existente_ci'}, status=status.HTTP_400_BAD_REQUEST)
        tutor_obj = crear_usuario_persona_rol(tutor_data, rol='tutor', ocupacion=tutor_data.get('ocupacion', ''))

    # Relacionar tutor con alumno (sin duplicar relación activa)
    ta, created = TutorAlumno.objects.get_or_create(
        tutor=tutor_obj,
        alumno=alumno_obj,
        defaults={'tipo_relacion': tipo_relacion, 'activo': True}
    )
    if not created and not ta.activo:
        ta.activo = True
        ta.tipo_relacion = tipo_relacion
        ta.save()

    # Crear inscripción en sección-grado solo si no está ya inscrito en ese ciclo/sección
    from apps.secciones.models import SeccionGrado, SeccionAlumno
    try:
        seccion_grado = SeccionGrado.objects.get(id=seccion_grado_id)
    except SeccionGrado.DoesNotExist:
        return Response({'error': 'La sección-grado seleccionada no existe'}, status=status.HTTP_400_BAD_REQUEST)
    if SeccionAlumno.objects.filter(alumno=alumno_obj, seccion_grado=seccion_grado, ciclo=ciclo, estado='activo').exists():
        return Response({'error': 'El alumno ya está inscrito en esta sección y ciclo'}, status=status.HTTP_400_BAD_REQUEST)
    seccion_alumno = SeccionAlumno(
        fecha_inscripcion=date.today(),
        ciclo=ciclo,
        estado='activo',
        seccion_grado=seccion_grado,
        alumno=alumno_obj
    )
    # Validar con el serializer de SeccionAlumno
    from apps.secciones.serializers import SeccionAlumnoSerializer
    serializer = SeccionAlumnoSerializer(data={
        'fecha_inscripcion': seccion_alumno.fecha_inscripcion,
        'ciclo': ciclo,
        'estado': 'activo',
        'seccion_grado': seccion_grado.id,
        'alumno': alumno_obj.id
    })
    serializer.is_valid(raise_exception=True)
    seccion_alumno.save()

    # Respuesta (Eliminar en producción)
    resp = {
        "mensaje": "Inscripción exitosa",
        "alumno": {
            "registro": alumno_obj.registro,
            "username": alumno_obj.persona.usuario.username,
            "password": alumno_obj.persona.ci
        },
        "tutor": {
            "username": tutor_obj.persona.usuario.username,
            "password": tutor_obj.persona.ci
        }
    }
    return Response(resp, status=status.HTTP_201_CREATED)

@extend_schema(responses=None) 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_usuario(request):
    user = request.user 
    try:
        persona = user.persona
    except Exception:
        persona = None
    
    # Permisos (privilegios)
    user_permissions = list(user.get_all_permissions())
    # Grupos (roles)
    user_groups = list(user.groups.values_list('name', flat=True))

    data = {
        'id': user.id,
        'username': user.username,
        'is_superuser': user.is_superuser,
        'privilegios': user_permissions,
        'roles': user_groups,
    }
    # Verificar tipo de persona y agregar detalles anidados
    if hasattr(persona, 'alumno') and persona.alumno is not None:
        data['alumno'] = AlumnoSerializer(persona.alumno).data
    if hasattr(persona, 'maestro') and persona.maestro is not None:
        data['maestro'] = MaestroSerializer(persona.maestro).data
    if hasattr(persona, 'tutor') and persona.tutor is not None:
        data['tutor'] = TutorSerializer(persona.tutor).data
        # Alumnos asociados a este tutor
        alumnos = persona.tutor.alumnos_asociados.all()
    return Response(data)

class RegisterFCMToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        user = request.user
        if token:
            # Si el token ya existe, actualizar el usuario asociado
            obj, created = FCMToken.objects.update_or_create(
                token=token,
                defaults={'user': user}
            )
            return Response({'status': 'ok', 'created': created})
        return Response({'error': 'No token'}, status=400)

class EnviarNotificacionAlumnoTutores(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        alumno_id = request.data.get('alumno_id')
        mensaje = request.data.get('mensaje')
        titulo = request.data.get('titulo', 'Alerta de predicción')
        porcentaje = request.data.get('porcentaje')
        data = request.data.get('data', {})
        if not alumno_id or not mensaje:
            return Response({'error': 'alumno_id y mensaje son requeridos'}, status=400)
        try:
            from apps.personas.models import Alumno, TutorAlumno, FCMToken
            alumno = Alumno.objects.get(id=alumno_id)
            user_alumno = alumno.persona.usuario
            # Tokens del alumno
            tokens_alumno = FCMToken.objects.filter(user=user_alumno)
            # Tokens de tutores
            tutores = TutorAlumno.objects.filter(alumno=alumno, activo=True).select_related('tutor__persona__usuario')
            tokens_tutores = FCMToken.objects.filter(user__in=[t.tutor.persona.usuario for t in tutores])
            # Enviar a todos los tokens
            for t in list(tokens_alumno) + list(tokens_tutores):
                # Convertir todos los valores de data a string para FCM
                data_str = {k: str(v) if v is not None else '' for k, v in {**data, "tipo": "alerta_prediccion", "mensaje": mensaje, "porcentaje": str(porcentaje) if porcentaje else ""}.items()}
                send_fcm_v1_notification(
                    t.token,
                    title=titulo,
                    body=f"{mensaje} (Probabilidad: {porcentaje}%)" if porcentaje else mensaje,
                    data=data_str
                )
            return Response({'status': 'ok'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)