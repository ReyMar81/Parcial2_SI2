from rest_framework.routers import DefaultRouter
from apps.secciones.views import GradoViewSet, SeccionViewSet, SeccionAlumnoViewSet, ResultadoFinalSeccionViewSet

router = DefaultRouter()
router.register(r'grados', GradoViewSet, basename='grado')
router.register(r'secciones', SeccionViewSet, basename='seccion')
router.register(r'seccion-alumnos', SeccionAlumnoViewSet, basename='seccionalumno')
router.register(r'resultado-final-seccion', ResultadoFinalSeccionViewSet, basename='resultadofinalseccion')

urlpatterns = router.urls
