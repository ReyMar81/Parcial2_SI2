from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()
class PrivilegioSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='name')
    codigo = serializers.CharField(source='codename')
    class Meta:
        model = Permission
        fields = ['id', 'nombre', 'codigo']

class RolSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='name')
    privilegios = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), source='permissions'
    )
    class Meta:
        model = Group
        fields = ['id', 'nombre', 'privilegios']

class UsuarioSerializer(serializers.ModelSerializer):
    roles = RolSerializer(source='groups', many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'roles']