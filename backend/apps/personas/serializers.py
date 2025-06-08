from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from apps.personas.models import Persona, Alumno, Maestro, Tutor, TutorAlumno
from apps.personas.services import crear_usuario_persona_rol

# --- PersonaSerializer ---
class PersonaSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    activo = serializers.BooleanField(required=False) 

    class Meta:
        model = Persona
        fields = '__all__'
        extra_kwargs = {
            'ci': {'validators': []},
        }

    def validate_ci(self, value):
        value = value.strip().upper()
        qs = Persona.objects.filter(ci__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe una persona registrada con este CI.")
        return value

    def to_internal_value(self, data):
        # Permite updates anidados sin problemas de unicidad.
        if 'id' in data and not self.instance:
            try:
                self.instance = Persona.objects.get(id=data['id'])
            except Persona.DoesNotExist:
                pass
        return super().to_internal_value(data)

# --- AlumnoSerializer ---
class AlumnoSerializer(WritableNestedModelSerializer):
    persona = PersonaSerializer()
    activo = serializers.BooleanField(required=False)

    class Meta:
        model = Alumno
        fields = ['id', 'persona', 'registro', 'activo']

    def create(self, validated_data):
        persona_data = validated_data.pop('persona')
        return crear_usuario_persona_rol(persona_data, rol='alumno')

# --- MaestroSerializer ---
class MaestroSerializer(WritableNestedModelSerializer):
    persona = PersonaSerializer()
    registro = serializers.CharField(read_only=True)
    activo = serializers.BooleanField(required=False)

    class Meta:
        model = Maestro
        fields = ['id', 'persona', 'registro', 'especialidad', 'activo']

    def create(self, validated_data):
        persona_data = validated_data.pop('persona')
        especialidad = validated_data.get('especialidad')
        return crear_usuario_persona_rol(persona_data, rol='maestro', especialidad=especialidad)

# --- TutorSerializer ---
class TutorSerializer(WritableNestedModelSerializer):
    persona = PersonaSerializer()
    alumnos_asociados = serializers.SerializerMethodField()
    activo = serializers.BooleanField(required=False)

    class Meta:
        model = Tutor
        fields = ['id', 'persona', 'ocupacion', 'alumnos_asociados', 'activo']

    def get_alumnos_asociados(self, obj):
        # Solo relaciones activas
        return [AlumnoSerializer(ta.alumno).data for ta in obj.alumnos_asociados.filter(activo=True)]

    def create(self, validated_data):
        persona_data = validated_data.pop('persona')
        ocupacion = validated_data.get('ocupacion')
        return crear_usuario_persona_rol(persona_data, rol='tutor', ocupacion=ocupacion)

# --- Serializer simple sin modelo (solo para validación de datos de inscripción) ---
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

# --- Serializador para relación Tutor-Alumno ---
class TutorAlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorAlumno
        fields = '__all__'

# --- Serializador de Inscripción con datos anidados ---
class InscripcionSerializer(serializers.Serializer):
    alumno = PersonaSerializer()
    tutor = TutorPersonaSerializer()
    tipo_relacion = serializers.CharField()
    seccion_id = serializers.IntegerField(write_only=True)
    ciclo = serializers.CharField()

# --- Serializer simple para actualizar alumnos de un tutor ---
class ActualizarAlumnosTutorSerializer(serializers.Serializer):
    alumnos_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
