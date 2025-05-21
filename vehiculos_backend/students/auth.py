from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, login
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from students.models import Estudiante, Entrada
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
        
    
class SimpleEntry(APIView):
    def post(self, request, matricula=None):
        print("\n=== Debug SimpleEntry ===")
        print(f"Content-Type: {request.content_type}")
        print(f"Request Method: {request.method}")
        print(f"Request Data: {request.data}")
        print(f"URL Matrícula: {matricula}")
        
        try:
            # Validar formato de datos
            if not isinstance(request.data, dict):
                print("Error: request.data no es un diccionario")
                return Response({
                    "error": "Formato de datos inválido",
                    "details": "Se esperaba un objeto JSON"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Si no viene en la URL, intentar obtener del body
            if not matricula:
                matricula = request.data.get('matricula')
                print(f"Matrícula del body: {matricula}")
            
            if not matricula:
                print("Error: No se proporcionó matrícula")
                return Response({
                    "error": "Se requiere matrícula del estudiante",
                    "details": "La matrícula no fue proporcionada en la URL ni en el cuerpo de la solicitud"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Verificar campos requeridos - aceptar tanto 'placa' como 'placas'
            placas = request.data.get('placas') or request.data.get('placa')
            print(f"Placas recibidas: {placas}")
            
            if not placas:
                print("Error: No se proporcionaron placas")
                return Response({
                    "error": "Se requiere el número de placas",
                    "details": "El campo 'placas' o 'placa' es obligatorio"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si existe el estudiante
            try:
                print(f"Buscando estudiante con matrícula: {matricula}")
                estudiante = Estudiante.objects.get(matricula=matricula)
                print(f"Estudiante encontrado: {estudiante.nombre}")
            except Estudiante.DoesNotExist:
                print(f"Error: No se encontró estudiante con matrícula {matricula}")
                return Response({
                    "error": f"No se encontró estudiante con matrícula {matricula}",
                    "details": "El estudiante no está registrado en el sistema"
                }, status=status.HTTP_404_NOT_FOUND)

            # Crear nuevo registro de entrada
            try:
                print("Creando registro de entrada...")
                entrada = Entrada.objects.create(
                    estudiante=estudiante,
                    placas=str(placas).upper(),  # Asegurar que sea string y convertir a mayúsculas
                    entrada=request.data.get('entrada', ''),
                    acciones=request.data.get('acciones', 'activo')
                )
                print(f"Entrada creada con ID: {entrada.id}")
            except Exception as e:
                print(f"Error al crear entrada: {str(e)}")
                return Response({
                    "error": "Error al crear el registro de entrada",
                    "details": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Respuesta exitosa
            response_data = {
                "message": "Entrada registrada exitosamente",
                "entrada_id": entrada.id,
                "datos": {
                    "estudiante": estudiante.matricula,
                    "placas": entrada.placas,
                    "entrada": entrada.entrada,
                    "acciones": entrada.acciones
                }
            }
            print(f"Respuesta exitosa: {response_data}")
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error interno del servidor: {str(e)}")
            return Response({
                "error": "Error interno del servidor",
                "details": str(e),
                "request_data": request.data
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SimpleExit(APIView):
    def post(self, request, matricula=None):
        print("\n=== Debug SimpleExit ===")
        print(f"Content-Type: {request.content_type}")
        print(f"Request Method: {request.method}")
        print(f"Request Data: {request.data}")
        print(f"URL Matrícula: {matricula}")
        
        try:
            # Verificar campos requeridos
            placas = request.data.get('placas') or request.data.get('placa')
            print(f"Placas recibidas: {placas}")
            
            if not placas:
                print("Error: No se proporcionaron placas")
                return Response({
                    "error": "Se requiere el número de placas",
                    "details": "El campo 'placas' o 'placa' es obligatorio"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Buscar la entrada activa por placas
            try:
                entrada = Entrada.objects.get(
                    placas=str(placas).upper(),
                    acciones='activo'
                )
                print(f"Entrada encontrada: {entrada.id}")
                estudiante = entrada.estudiante
                print(f"Estudiante asociado: {estudiante.matricula}")
                
            except Entrada.DoesNotExist:
                print(f"No se encontró entrada activa para las placas: {placas}")
                return Response({
                    "error": "No se encontró registro activo",
                    "details": f"No hay un registro activo para las placas {placas}"
                }, status=status.HTTP_404_NOT_FOUND)

            # Actualizar el estado de la entrada
            entrada.acciones = 'inactivo'
            entrada.save()
            print(f"Entrada actualizada: {entrada.id}")

            return Response({
                "message": "Salida registrada exitosamente",
                "datos": {
                    "estudiante": estudiante.matricula,
                    "placas": entrada.placas,
                    "entrada": entrada.entrada
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error en salida: {str(e)}")
            return Response({
                "error": "Error interno del servidor",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VehiculosActivos(APIView):
    def get(self, request, matricula=None):
        try:
            estudiante = Estudiante.objects.filter(matricula=matricula).first()
            if not estudiante:
                return Response({
                    "error": f"No se encontró estudiante con matrícula {matricula}"
                }, status=status.HTTP_404_NOT_FOUND)

            entradas_activas = Entrada.objects.filter(
                estudiante=estudiante,
                acciones='activo'
            ).values('placas', 'entrada')

            return Response({
                "message": "Vehículos activos encontrados",
                "vehiculos": list(entradas_activas)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error al obtener vehículos activos",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class VehiculosHistorial(APIView):
    def get(self, request, matricula=None):
        try:
            estudiante = Estudiante.objects.filter(matricula=matricula).first()
            if not estudiante:
                return Response({
                    "error": f"No se encontró estudiante con matrícula {matricula}"
                }, status=status.HTTP_404_NOT_FOUND)

            historial = Entrada.objects.filter(
                estudiante=estudiante
            ).order_by('-entrada').values('placas', 'entrada', 'acciones')

            return Response({
                "message": "Historial de vehículos encontrado",
                "historial": list(historial)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error al obtener historial",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class UserRegistration(APIView):
    def post(self, request):
        print("\n=== DEBUG: Iniciando proceso de registro de usuario ===")
        print("Datos recibidos en request.data:", request.data)
        print("Content-Type:", request.content_type)
        print("Método:", request.method)

        # Validar campos requeridos
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        print("\nVerificando campos requeridos...")
        for field in required_fields:
            if not request.data.get(field):
                print(f"ERROR: Campo faltante: {field}")
                return Response({
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        print("Todos los campos requeridos están presentes")

        try:
            # Verificar si el usuario ya existe
            User = get_user_model()
            print(f"\nVerificando si existe usuario con email: {request.data['email']}")
            if User.objects.filter(email=request.data['email']).exists():
                print(f"ERROR: Ya existe un usuario con el email {request.data['email']}")
                return Response({
                    'error': 'Ya existe un usuario con este email'
                }, status=status.HTTP_400_BAD_REQUEST)
            print("Email disponible para registro")

            # Crear el usuario
            print("\nCreando nuevo usuario...")
            user = User.objects.create_user(
                username=request.data['username'],
                email=request.data['email'],
                password=request.data['password'],
                first_name=request.data['first_name'].strip(),
                last_name=request.data['last_name'].strip()
            )
            print(f"Usuario creado exitosamente con ID: {user.id}")

            # Crear el registro de estudiante
            print("\nCreando registro de estudiante...")
            nombre_completo = f"{request.data['first_name'].strip()} {request.data['last_name'].strip()}"
            print(f"Nombre completo: {nombre_completo}")
            print(f"Email: {request.data['email']}")
            print(f"Matrícula a usar: {request.data['password']}")

            estudiante = Estudiante.objects.create(
                email=request.data['email'],
                nombre=nombre_completo,
                matricula=request.data['password']
            )
            print(f"Estudiante creado exitosamente con ID: {estudiante.id}")

            print("\n=== Registro completado exitosamente ===")
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user_id': user.id,
                'email': user.email,
                'matricula': estudiante.matricula,
                'nombre': nombre_completo
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"\nERROR CRÍTICO en el proceso de registro:")
            print(f"Tipo de error: {type(e).__name__}")
            print(f"Mensaje de error: {str(e)}")
            print("Traceback completo:", e.__traceback__)
            return Response({
                'error': 'Error al registrar usuario',
                'tipo_error': type(e).__name__,
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)