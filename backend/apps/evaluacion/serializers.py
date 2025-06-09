from rest_framework import serializers
from apps.evaluacion.models import Nota, Asistencia, Participacion, TipoNota

class NotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nota
        fields = '__all__'

    def validate(self, data):
        alumno = data['alumno']
        tipo_nota = data['tipo_nota']
        materia_asignada = data['materia_asignada']
        calificacion = data['calificacion']

        # La nota solo puede estar entre 0 y 100
        if not (0 <= calificacion <= 100):
            raise serializers.ValidationError('La calificación debe estar entre 0 y 100.')

        # Validar que el tipo_nota pertenece a la misma materia_asignada
        if tipo_nota.materia_asignada != materia_asignada:
            raise serializers.ValidationError('El tipo de nota no corresponde a la materia asignada.')

        # Validar inscripción
        if materia_asignada.seccion_grado.seccion not in [insc.seccion_grado.seccion for insc in alumno.inscripciones.all()]:
            raise serializers.ValidationError('El alumno no está inscrito en la sección asignada a la materia.')

        return data
        
class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = '__all__'

    def validate(self, data):
        alumno = data['alumno']
        materia_asignada = data['materia_asignada']
        fecha = data['fecha']
        estado = data['estado'].lower()
        ESTADOS_VALIDOS = ['presente', 'ausente', 'justificado']

        if estado not in ESTADOS_VALIDOS:
            raise serializers.ValidationError(f"Estado inválido. Opciones: {', '.join(ESTADOS_VALIDOS)}")

        # Validar inscripción (corregido: usar seccion_grado.seccion)
        if materia_asignada.seccion_grado.seccion not in [insc.seccion_grado.seccion for insc in alumno.inscripciones.all()]:
            raise serializers.ValidationError('El alumno no está inscrito en la sección asignada a la materia.')

        return data

from .models import Participacion

class ParticipacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participacion
        fields = '__all__'

    def validate(self, data):
        alumno = data['alumno']
        materia_asignada = data['materia_asignada']
        puntaje = data['puntaje']

        if not (0 <= puntaje <= 10):
            raise serializers.ValidationError('El puntaje debe estar entre 0 y 10.')

        if materia_asignada.seccion_grado.seccion not in [insc.seccion_grado.seccion for insc in alumno.inscripciones.all()]:
            raise serializers.ValidationError('El alumno no está inscrito en la sección asignada a la materia.')
        
        return data
