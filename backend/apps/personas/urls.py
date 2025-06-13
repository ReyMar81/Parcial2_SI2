from rest_framework.routers import DefaultRouter
from .views import PersonaViewSet, AlumnoViewSet, MaestroViewSet, TutorViewSet, TutorAlumnoViewSet, perfil_usuario, inscripcion, RegisterFCMToken, EnviarNotificacionAlumnoTutores
from django.urls import path

router = DefaultRouter()
router.register(r'personas', PersonaViewSet, basename='persona')
router.register(r'alumnos', AlumnoViewSet, basename='alumno')
router.register(r'maestros', MaestroViewSet, basename='maestro')
router.register(r'tutores', TutorViewSet, basename='tutor')
router.register(r'tutor-alumnos', TutorAlumnoViewSet, basename='tutoralumno')

urlpatterns = router.urls

urlpatterns += [
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('inscripcion/', inscripcion, name='inscripcion'),
    path('fcm/register/', RegisterFCMToken.as_view(), name='register-fcm-token'),
    path('enviar-notificacion-alumno-tutores/', EnviarNotificacionAlumnoTutores.as_view(), name='enviar-notificacion-alumno-tutores'),
]