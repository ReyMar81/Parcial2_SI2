from rest_framework.routers import DefaultRouter
from apps.evaluacion.views import NotaViewSet, AsistenciaViewSet, ParticipacionViewSet

router = DefaultRouter()
router.register(r'notas', NotaViewSet, basename='nota')
router.register(r'asistencias', AsistenciaViewSet, basename='asistencia')
router.register(r'participaciones', ParticipacionViewSet, basename='participacion')

urlpatterns = router.urls
