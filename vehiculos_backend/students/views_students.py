from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import csv
from io import TextIOWrapper
from django.db import transaction
from .models import Estudiante
from .serializers import EstudianteSerializer, CSVUploadSerializer

class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer
    parser_classes = (MultiPartParser,)

    @action(detail=False, methods=['post'], serializer_class=CSVUploadSerializer)
    def upload_csv(self, request):
        serializer = CSVUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        archivo = request.FILES['archivo']
        registros_creados = 0
        errores = []

        try:
            with TextIOWrapper(archivo.file, encoding='utf-8') as csvfile:
                lector = csv.DictReader(csvfile)
                with transaction.atomic():
                    for fila_num, fila in enumerate(lector, start=1):
                        try:
                            Estudiante.objects.update_or_create(
                                matricula=fila['Matricula'],
                                defaults={
                                    'apellido_paterno': fila['Apellido Paterno'],
                                    'apellido_materno': fila['Apellido Materno'],
                                    'nombre': fila['Nombre'],
                                    'email': fila['Email']
                                }
                            )
                            registros_creados += 1
                        except Exception as e:
                            errores.append(f"Fila {fila_num}: {str(e)}")
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        resultado = {
            'registros_creados': registros_creados,
            'errores': errores
        }
        return Response(resultado, status=status.HTTP_201_CREATED)