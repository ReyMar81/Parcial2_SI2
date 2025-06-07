from rest_framework import serializers
from apps.personas.models import Persona, Alumno, Maestro, Tutor, TutorAlumno
from apps.personas.services import crear_usuario_persona_rol

class PersonaSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Persona
        fields = '__all__'

class AlumnoSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer()
    class Meta:
        model = Alumno
        fields = ['id', 'persona', 'registro']
    def create(self, validated_data):
        persona_data = validated_data.pop('persona')
        return crear_usuario_persona_rol(persona_data, rol='alumno')

class MaestroSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer()
    class Meta:
        model = Maestro
        fields = ['id', 'persona', 'registro', 'especialidad']
    def create(self, validated_data):
        persona_data = validated_data.pop('persona')
        especialidad = validated_data.get('especialidad')
        return crear_usuario_persona_rol(persona_data, rol='maestro', especialidad=especialidad)

class TutorSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer()
    class Meta:
        model = Tutor
        fields = ['id', 'persona', 'ocupacion']
    def create(self, validated_data):
        persona_data = validated_data.pop('persona')
        ocupacion = validated_data.get('ocupacion')
        return crear_usuario_persona_rol(persona_data, rol='tutor', ocupacion=ocupacion)

class TutorPersonaSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    apellido_paterno = serializers.CharField()
    apellido_materno = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    genero = serializers.CharField()
    ci = serializers.CharField()
    direccion = serializers.CharField()
    contacto = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fecha_nacimiento = serializers.DateField()
    ocupacion = serializers.CharField()

class TutorAlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorAlumno
        fields = '__all__'

class InscripcionSerializer(serializers.Serializer):
    alumno = PersonaSerializer()
    tutor = TutorPersonaSerializer()
    tipo_relacion = serializers.CharField()
    seccion_id = serializers.IntegerField(write_only=True)
    ciclo = serializers.CharField()