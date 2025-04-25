from rest_framework import viewsets, filters
from .models import Vehiculo
from .serializers import VehiculoSerializer

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['matricula', 'nombre', 'apellido_paterno', 'apellido_materno', 'placa']
    ordering_fields = '__all__'