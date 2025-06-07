from rest_framework import serializers
from apps.secciones.models import Grado, Seccion, SeccionAlumno, ResultadoFinalSeccion
from apps.materias.models import MateriaAsignada, ResultadoFinalMateria

class GradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grado
        fields = '__all__'

class SeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seccion
        fields = '__all__'

class SeccionAlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeccionAlumno
        fields = '__all__'

    def validate(self, data):
        alumno = data['alumno']
        ciclo = data['ciclo']
        seccion = data['seccion']

        # Verificar que no exista ya inscripción activa para este alumno, ciclo y sección
        existe = SeccionAlumno.objects.filter(
            alumno=alumno,
            ciclo=ciclo,
            estado='activo'
        )
        if existe.exists():
            raise serializers.ValidationError(
                'Este alumno ya está inscrito activamente en una sección para este ciclo escolar.'
            )

        # Validación de capacidad máxima de la sección
        inscritos = SeccionAlumno.objects.filter(seccion=seccion, ciclo=ciclo, estado='activo').count()
        if inscritos >= seccion.capacidad_maxima:
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