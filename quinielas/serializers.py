from rest_framework import serializers
from .models import Quiniela


class QuinielaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiniela
        fields = '__all__'
        read_only_fields = ['slug', 'creado_en']
