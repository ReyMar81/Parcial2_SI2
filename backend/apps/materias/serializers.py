from rest_framework import serializers
from apps.materias.models import Materia, MateriaAsignada, ResultadoFinalMateria, TipoNota

class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = '__all__'

class MateriaAsignadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MateriaAsignada
        fields = '__all__'

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

        # Cálculo del promedio ponderado
        tipos_nota = TipoNota.objects.filter(materia_asignada=materia_asignada)
        notas = Nota.objects.filter(alumno=alumno, materia_asignada=materia_asignada)
        suma_ponderada = 0
        suma_pesos = 0
        for tipo in tipos_nota:
            nota = notas.filter(tipo_nota=tipo).first()
            if nota:
                suma_ponderada += nota.calificacion * tipo.peso
                suma_pesos += tipo.peso
        if suma_pesos > 0:
            promedio = suma_ponderada / suma_pesos
            data['promedio'] = promedio
            data['aprobado'] = promedio >= 51
        else:
            raise serializers.ValidationError(
                'No hay notas suficientes para calcular el promedio final.'
            )
        return data