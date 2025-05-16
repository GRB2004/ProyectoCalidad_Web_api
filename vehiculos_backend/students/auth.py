from django.contrib.auth.models import User
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

        email = request.data.get('email')
        matricula = request.data.get('matricula')

        if not email or not matricula:
            return Response({
                "error": "Datos incompletos",
                "details": "Se requiere email y matrícula"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar al estudiante por matrícula y email
            estudiante = Estudiante.objects.get(matricula=matricula, email=email)
            
            # Crear sesión
            request.session['estudiante_id'] = estudiante.id
            request.session['matricula'] = estudiante.matricula
            
            # Devolver datos del estudiante
            estudiante_data = CSVUploadSerializer(estudiante).data
            
            return Response({
                "message": "Inicio de sesión exitoso",
                "estudiante": estudiante_data
            }, status=status.HTTP_200_OK)

        except Estudiante.DoesNotExist:
            return Response({
                "error": "Credenciales inválidas",
                "details": "La matrícula o el email no coinciden con nuestros registros"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return Response({
                "error": "Error en el servidor",
                "details": str(e)
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