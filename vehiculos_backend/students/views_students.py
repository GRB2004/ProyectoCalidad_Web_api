from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import csv
from io import TextIOWrapper
from django.db import transaction
from .models import Estudiante
from .serializers import EstudianteSerializer, CSVUploadSerializer
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

class EstudiantePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer
    parser_classes = (MultiPartParser,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'matricula',
        'apellido_paterno',
        'apellido_materno',
        'nombre',
        'email'
    ]
    ordering_fields = '__all__'
    pagination_class = EstudiantePagination

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
    
    # Nueva acción para búsqueda personalizada
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        term = request.query_params.get('q', '')
        queryset = self.filter_queryset(self.get_queryset())
        
        if term:
            queryset = queryset.filter(
                Q(matricula__icontains=term) |
                Q(apellido_paterno__icontains=term) |
                Q(apellido_materno__icontains=term) |
                Q(nombre__icontains=term) |
                Q(email__icontains=term)
            )
            
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)