from rest_framework import serializers
from .models import Quiniela, Seleccion, Participante, Bombo, DIVISORES_48


class SeleccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seleccion
        fields = ['id', 'nombre']


class BomboSerializer(serializers.ModelSerializer):
    paises = SeleccionSerializer(source='seleccion_set', many=True, read_only=True)

    class Meta:
        model = Bombo
        fields = ['numero', 'paises']


class ParticipanteSerializer(serializers.ModelSerializer):
    selecciones = SeleccionSerializer(many=True, read_only=True)

    class Meta:
        model = Participante
        fields = '__all__'
        read_only_fields = ['quiniela', 'selecciones', 'fecha_union']


class QuinielaSerializer(serializers.ModelSerializer):
    participantes = ParticipanteSerializer(many=True, read_only=True)

    class Meta:
        model = Quiniela
        fields = '__all__'
        read_only_fields = ['slug', 'creado_en', 'sorteada']

    def validate_numero_participantes(self, value):
        if value not in DIVISORES_48:
            raise serializers.ValidationError(
                f"Debe ser divisor de 48: {DIVISORES_48}"
            )
        return value
