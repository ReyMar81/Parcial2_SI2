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

        # Solo una nota por alumno/tipo_nota
        if Nota.objects.filter(alumno=alumno, tipo_nota=tipo_nota).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError('Ya existe una nota para este alumno y tipo de nota.')

        # Validar que el tipo_nota pertenece a la misma materia_asignada
        if tipo_nota.materia_asignada != materia_asignada:
            raise serializers.ValidationError('El tipo de nota no corresponde a la materia asignada.')

        # Validar inscripción
        if materia_asignada.seccion not in [insc.seccion for insc in alumno.inscripciones.all()]:
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

        if Asistencia.objects.filter(
            alumno=alumno,
            materia_asignada=materia_asignada,
            fecha=fecha
        ).exists():
            raise serializers.ValidationError('Ya se registró asistencia para este alumno y materia en esa fecha.')
        
        if materia_asignada.seccion not in [insc.seccion for insc in alumno.inscripciones.all()]:
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

        if materia_asignada.seccion not in [insc.seccion for insc in alumno.inscripciones.all()]:
            raise serializers.ValidationError('El alumno no está inscrito en la sección asignada a la materia.')
        
        return data
