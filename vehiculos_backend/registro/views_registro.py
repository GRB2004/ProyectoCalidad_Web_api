from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import RegistroActivo, RegistroHistorial
from .serializers import RegistroActivoSerializer, RegistroHistorialSerializer
from django.utils import timezone
from datetime import timedelta

class RegistroActivoViewSet(viewsets.ModelViewSet):
    queryset = RegistroActivo.objects.all()
    serializer_class = RegistroActivoSerializer

    @action(detail=True, methods=['post'])
    def registrar_salida(self, request, pk=None):
        registro = self.get_object()
        try:
            exit_time = timezone.now()
            duration = exit_time - registro.entry_time
            
            # Crear registro histórico
            RegistroHistorial.objects.create(
                placa=registro.placa,
                estudiante_matricula=registro.estudiante_matricula,
                entry_time=registro.entry_time,
                exit_time=exit_time,
                duration=duration
            )
            
            # Eliminar registro activo
            registro.delete()
            
            return Response({'status': 'Salida registrada'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RegistroHistorialViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistroHistorialSerializer
    queryset = RegistroHistorial.objects.all()
    
    def get_queryset(self):
        matricula = self.request.query_params.get('matricula', None)
        if matricula:
            return RegistroHistorial.objects.filter(estudiante_matricula=matricula)
        return RegistroHistorial.objects.all()