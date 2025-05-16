from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, login
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from students.models import Estudiante
from students.serializers import CSVUploadSerializer

class SimpleLogin(APIView):
    def post(self, request):
        print("=== Iniciando proceso de autenticación simple ===")
        print("Datos recibidos:", request.data)
        
        email = request.data.get('username')
        matricula = request.data.get('password')  # La contraseña es la matrícula
        
        print(f"Email recibido: {email}")
        print(f"Matrícula recibida: {matricula}")
        
        if not email or not matricula:
            return Response({
                'error': 'Se requieren email y matrícula'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        User = get_user_model()
        try:
            # Primero buscamos si existe el usuario con ese email
            user = User.objects.get(email=email)
            print(f"Usuario encontrado: {user.username}")
            
            # Buscamos el estudiante asociado al usuario
            try:
                estudiante = Estudiante.objects.get(email=email)
                # Verificamos si la matrícula coincide
                if estudiante.matricula == matricula:
                    login(request, user)
                    return Response({
                        'message': 'Login exitoso',
                        'user_id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'matricula': estudiante.matricula
                    })
                else:
                    print(f"Matrícula incorrecta. Esperada: {estudiante.matricula}, Recibida: {matricula}")
                    return Response({
                        'error': 'Matrícula incorrecta'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Estudiante.DoesNotExist:
                print(f"No se encontró estudiante con email: {email}")
                return Response({
                    'error': 'No existe estudiante con este email'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            print(f"No se encontró usuario con email: {email}")
            return Response({
                'error': f'No existe usuario con el email {email}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return Response({
                'error': 'Error en el servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SimpleLogout(APIView):
    def post(self, request):
        try:
            request.session.flush()
            return Response({
                "message": "Sesión cerrada exitosamente"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error en logout: {str(e)}")
            return Response({
                "error": "Error al cerrar sesión"
            }, status=status.HTTP_400_BAD_REQUEST)
        

class StudentSearch(APIView):
    def get(self, request):
        try:
            search_type = request.query_params.get('type')
            search_value = request.query_params.get('value')

            if not search_type or not search_value:
                return Response({
                    "error": "Parámetros incompletos",
                    "details": "Se requiere tipo de búsqueda (email/matricula) y valor"
                }, status=status.HTTP_400_BAD_REQUEST)

            if search_type not in ['email', 'matricula']:
                return Response({
                    "error": "Tipo de búsqueda inválido",
                    "details": "El tipo debe ser 'email' o 'matricula'"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Construir el filtro dinámicamente
            filter_kwargs = {search_type: search_value}
            estudiante = Estudiante.objects.filter(**filter_kwargs).first()

            if not estudiante:
                return Response({
                    "error": "No encontrado",
                    "details": f"No se encontró estudiante con {search_type}: {search_value}"
                }, status=status.HTTP_404_NOT_FOUND)

            estudiante_data = CSVUploadSerializer(estudiante).data
            return Response({
                "message": "Estudiante encontrado",
                "estudiante": estudiante_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error en búsqueda: {str(e)}")
            return Response({
                "error": "Error en el servidor",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)