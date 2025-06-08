from rest_framework import serializers
from apps.materias.models import Materia, MateriaAsignada, ResultadoFinalMateria, TipoNota
from apps.secciones.models import SeccionGrado
from apps.personas.serializers import MaestroSerializer
from apps.materias.models import Materia
from apps.personas.models import Maestro
from apps.secciones.serializers import SeccionGradoSerializer

class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = '__all__'

class MateriaAsignadaSerializer(serializers.ModelSerializer):
    materia_id = serializers.PrimaryKeyRelatedField(queryset=Materia.objects.all(), source='materia', write_only=True)
    maestro_id = serializers.PrimaryKeyRelatedField(queryset=Maestro.objects.all(), source='maestro', write_only=True)
    seccion_grado_id = serializers.PrimaryKeyRelatedField(queryset=SeccionGrado.objects.all(), source='seccion_grado', write_only=True)

    materia = serializers.SerializerMethodField(read_only=True)
    maestro = serializers.SerializerMethodField(read_only=True)
    seccion_grado = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MateriaAsignada
        fields = [
            'id', 'ciclo', 'horas_semanales',
            'materia_id', 'maestro_id', 'seccion_grado_id',
            'materia', 'maestro', 'seccion_grado'
        ]

    def get_materia(self, obj):
        return {'id': obj.materia.id, 'nombre': obj.materia.nombre} if obj.materia else None

    def get_maestro(self, obj):
        if obj.maestro and obj.maestro.persona:
            nombre = obj.maestro.persona.nombre
            ap = obj.maestro.persona.apellido_paterno
            am = obj.maestro.persona.apellido_materno or ''
            nombre_completo = f"{nombre} {ap} {am}".strip()
            return {'id': obj.maestro.id, 'nombre': nombre_completo}
        return None

    def get_seccion_grado(self, obj):
        if obj.seccion_grado:
            nombre = f"{obj.seccion_grado.grado.nombre} - {obj.seccion_grado.seccion.nombre} ({obj.seccion_grado.aula})"
            return {'id': obj.seccion_grado.id, 'nombre': nombre}
        return None

class TipoNotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoNota
        fields = '__all__'

    def validate(self, data):
        materia_asignada = data['materia_asignada']
        nombre = data['nombre']
        qs = TipoNota.objects.filter(materia_asignada=materia_asignada, nombre=nombre)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe un tipo de nota con ese nombre para esta materia asignada.')
        return data
        
class ResultadoFinalMateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoFinalMateria
        fields = '__all__'

    def validate(self, data):
        alumno = data['alumno']
        materia_asignada = data['materia_asignada']
        ciclo = data['ciclo']

        # Duplicados
        existe = ResultadoFinalMateria.objects.filter(
            alumno=alumno,
            materia_asignada=materia_asignada,
            ciclo=ciclo
        )
        if self.instance:
            existe = existe.exclude(pk=self.instance.pk)
        if existe.exists():
            raise serializers.ValidationError(
                'Ya existe un resultado final para este alumno, materia y ciclo escolar.'
            )
        return data