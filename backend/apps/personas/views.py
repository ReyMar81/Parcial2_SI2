from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from apps.personas.models import Persona, Alumno, Maestro, Tutor, TutorAlumno
from apps.personas.serializers import PersonaSerializer, AlumnoSerializer, MaestroSerializer, TutorSerializer, TutorAlumnoSerializer, InscripcionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.personas.services import crear_usuario_persona_rol
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.secciones.models import Seccion, SeccionAlumno
from datetime import date

class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer

class AlumnoViewSet(viewsets.ModelViewSet):
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer

class MaestroViewSet(viewsets.ModelViewSet):
    queryset = Maestro.objects.all()
    serializer_class = MaestroSerializer

class TutorViewSet(viewsets.ModelViewSet):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer

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
    tipo_relacion = request.data.get('tipo_relacion', '')
    seccion_id = request.data.get('seccion_id')
    ciclo = request.data.get('ciclo')

    # Validaciones mínimas
    if not alumno_data or not tutor_data or not seccion_id or not ciclo:
        return Response({'error': 'Datos de alumno, tutor, sección y ciclo son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    # No permitir inscripción duplicada por CI
    from apps.personas.models import Persona
    if Persona.objects.filter(ci=alumno_data['ci']).exists():
        return Response({'error': 'Alumno ya inscrito (CI existente)'}, status=status.HTTP_400_BAD_REQUEST)
    if Persona.objects.filter(ci=tutor_data['ci']).exists():
        return Response({'error': 'El tutor ya tiene un usuario, use el endpoint para agregar un tutor existente'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Crear alumno y tutor
    alumno_obj = crear_usuario_persona_rol(alumno_data, rol='alumno')
    tutor_obj = crear_usuario_persona_rol(tutor_data, rol='tutor', ocupacion=tutor_data.get('ocupacion', ''))

    # Relacionar tutor con alumno
    ta = TutorAlumno.objects.create(
        tutor=tutor_obj,
        alumno=alumno_obj,
        tipo_relacion=tipo_relacion
    )

    # Crear inscripción en sección

    try:
        seccion = Seccion.objects.get(id=seccion_id)
    except Seccion.DoesNotExist:
        return Response({'error': 'La sección seleccionada no existe'}, status=status.HTTP_400_BAD_REQUEST)
    seccion_alumno = SeccionAlumno(
        fecha_inscripcion=date.today(),
        ciclo=ciclo,
        estado='activo',
        seccion=seccion,
        alumno=alumno_obj
    )
    # Validar con el serializer de SeccionAlumno
    from apps.secciones.serializers import SeccionAlumnoSerializer
    serializer = SeccionAlumnoSerializer(data={
        'fecha_inscripcion': seccion_alumno.fecha_inscripcion,
        'ciclo': ciclo,
        'estado': 'activo',
        'seccion': seccion.id,
        'alumno': alumno_obj.id
    })
    serializer.is_valid(raise_exception=True)
    seccion_alumno.save()

    # Respuesta (Eliminar en producción)
    resp = {
        "mensaje": "Inscripción exitosa",
        "alumno": {
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
    # Verificar tipo de persona y agregar detalles
    if hasattr(persona, 'alumno'):
        data['alumno'] = AlumnoSerializer(persona.alumno).data
    if hasattr(persona, 'maestro'):
        data['maestro'] = MaestroSerializer(persona.maestro).data
    if hasattr(persona, 'tutor'):
        data['tutor'] = TutorSerializer(persona.tutor).data
        # Alumnos asociados a este tutor
        alumnos = persona.tutor.alumnos_asociados.all()
        data['alumnos_asociados'] = [AlumnoSerializer(a.alumno).data for a in alumnos]
    
    return Response(data)