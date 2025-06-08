from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import GroupViewSet, PermissionViewSet, UsuarioRolViewSet, CustomTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'roles', GroupViewSet, basename='rol')
router.register(r'privilegios', PermissionViewSet, basename='privilegio')
router.register(r'usuarios-roles', UsuarioRolViewSet, basename='usuarios-roles')

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
