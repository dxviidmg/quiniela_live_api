from rest_framework import serializers
from .models import Quiniela, Seleccion, Participante, DIVISORES_48


class SeleccionSerializer(serializers.ModelSerializer):
    fase_display = serializers.CharField(source='get_fase_display', read_only=True)
    
    class Meta:
        model = Seleccion
        fields = ['id', 'nombre', 'code', 'eliminado', 'fase', 'fase_display', 'es_campeon', 'es_subcampeon', 'es_tercero']


class ParticipanteSerializer(serializers.ModelSerializer):
    selecciones = serializers.SerializerMethodField()

    def get_selecciones(self, obj):
        qs = obj.selecciones.order_by('eliminado', '-es_campeon', '-es_subcampeon', '-es_tercero', '-fase', 'pk')
        return SeleccionSerializer(qs, many=True).data

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
