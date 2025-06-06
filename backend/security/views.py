from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .serializers import RolSerializer, PrivilegioSerializer

User = get_user_model()
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAdminUser]

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PrivilegioSerializer
    permission_classes = [IsAdminUser]

class UsuarioRolViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        usuario = User.objects.get(pk=pk)
        grupos = usuario.groups.all()
        serializer = RolSerializer(grupos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def asignar_roles(self, request, pk=None):
        usuario = User.objects.get(pk=pk)
        roles_ids = request.data.get('roles', [])
        grupos = Group.objects.filter(id__in=roles_ids)
        usuario.groups.set(grupos)
        usuario.save()
        return Response({'estado': 'Roles actualizados correctamente.'}, status=status.HTTP_200_OK)
