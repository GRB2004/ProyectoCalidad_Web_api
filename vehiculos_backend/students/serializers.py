from rest_framework import serializers
from .models import Estudiante

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = '__all__'
        extra_kwargs = {
            'email': {'validators': []}  # Permite actualizar sin validar unique
        }

class CSVUploadSerializer(serializers.Serializer):
    archivo = serializers.FileField()