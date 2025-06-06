from rest_framework.routers import DefaultRouter
from apps.materias.views import MateriaViewSet, MateriaAsignadaViewSet, ResultadoFinalMateriaViewSet, TipoNotaViewSet

router = DefaultRouter()
router.register(r'materias', MateriaViewSet, basename='materia')
router.register(r'materias-asignadas', MateriaAsignadaViewSet, basename='materiaasignada')
router.register(r'resultado-final-materia', ResultadoFinalMateriaViewSet, basename='resultadofinalmateria')
router.register(r'tipos-nota', TipoNotaViewSet, basename='tiponota')

urlpatterns = router.urls
