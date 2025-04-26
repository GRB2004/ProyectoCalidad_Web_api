from rest_framework import serializers
from .models import RegistroActivo, RegistroHistorial

class RegistroActivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroActivo
        fields = '__all__'
        read_only_fields = ['entry_time']

class RegistroHistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroHistorial
        fields = '__all__'