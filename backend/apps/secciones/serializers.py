from rest_framework import serializers
from apps.secciones.models import Grado, Seccion, SeccionGrado, SeccionAlumno, ResultadoFinalSeccion
from apps.materias.models import MateriaAsignada, ResultadoFinalMateria

class GradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grado
        fields = '__all__'

class SeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seccion
        fields = '__all__'

class SeccionGradoSerializer(serializers.ModelSerializer):
    seccion_nombre = serializers.CharField(source='seccion.nombre', read_only=True)
    grado_nombre = serializers.CharField(source='grado.nombre', read_only=True)
    grado_id = serializers.PrimaryKeyRelatedField(queryset=Grado.objects.all(), source='grado', write_only=True)
    seccion_id = serializers.PrimaryKeyRelatedField(queryset=Seccion.objects.all(), source='seccion', write_only=True)

    class Meta:
        model = SeccionGrado
        fields = ['id', 'aula', 'capacidad_maxima', 'activo', 'seccion_id', 'grado_id', 'seccion_nombre', 'grado_nombre']

class SeccionAlumnoSerializer(serializers.ModelSerializer):
    seccion_grado_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SeccionAlumno
        fields = '__all__'
        extra_fields = ['seccion_grado_nombre']

    def get_seccion_grado_nombre(self, obj):
        return f"{obj.seccion_grado.grado.nombre} - {obj.seccion_grado.seccion.nombre} ({obj.seccion_grado.aula})"

    def validate(self, data):
        alumno = data['alumno']
        ciclo = data['ciclo']
        seccion_grado = data['seccion_grado']

        existe = SeccionAlumno.objects.filter(
            alumno=alumno,
            ciclo=ciclo,
            estado='activo'
        )
        if existe.exists():
            raise serializers.ValidationError(
                'Este alumno ya está inscrito activamente en una sección para este ciclo escolar.'
            )

        inscritos = SeccionAlumno.objects.filter(seccion_grado=seccion_grado, ciclo=ciclo, estado='activo').count()
        if inscritos >= seccion_grado.capacidad_maxima:
            raise serializers.ValidationError('La sección ya está llena.')

        # --- Validación de aprobación del ciclo anterior ---
        # Solo si NO es el primer ciclo
        try:
            ciclo_anterior = str(int(ciclo) - 1)
        except Exception:
            ciclo_anterior = None

        if ciclo_anterior:
            inscripciones_anteriores = SeccionAlumno.objects.filter(
                alumno=alumno,
                ciclo=ciclo_anterior
            )
            if inscripciones_anteriores.exists():
                aprobados = ResultadoFinalSeccion.objects.filter(
                    seccion_alumno__in=inscripciones_anteriores,
                    ciclo=ciclo_anterior,
                    aprobado=True
                )
                if not aprobados.exists():
                    raise serializers.ValidationError(
                        'El alumno no aprobó el ciclo anterior, no puede inscribirse en un nuevo ciclo.'
                    )

        return data

class ResultadoFinalSeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoFinalSeccion
        fields = '__all__'

    def validate(self, data):
        seccion_alumno = data['seccion_alumno']
        ciclo = data['ciclo']

        # Evitar duplicados
        existe = ResultadoFinalSeccion.objects.filter(
            seccion_alumno=seccion_alumno,
            ciclo=ciclo
        )
        if self.instance:
            existe = existe.exclude(pk=self.instance.pk)
        if existe.exists():
            raise serializers.ValidationError(
                'Ya existe un resultado final de sección para este alumno y ciclo escolar.'
            )

        alumno = seccion_alumno.alumno

        # Busca todas las materias asignadas a la sección y ciclo
        materias_asignadas = MateriaAsignada.objects.filter(
            seccion=seccion_alumno.seccion,
            ciclo=ciclo
        )

        # Busca los resultados finales de esas materias
        resultados_materia = ResultadoFinalMateria.objects.filter(
            alumno=alumno,
            materia_asignada__in=materias_asignadas,
            ciclo=ciclo
        )

        total_materias = materias_asignadas.count()
        materias_aprobadas = resultados_materia.filter(aprobado=True).count()

        # Regla: debe aprobar todas
        # Ejemplo: Debe aprobar todas
        aprobado = (total_materias > 0 and materias_aprobadas == total_materias)

        data['aprobado'] = aprobado

        if total_materias == 0:
            raise serializers.ValidationError('No se encontraron materias asignadas para calcular el resultado final.')
        return data