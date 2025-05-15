import os
import sys
import csv
import django # type: ignore
from django.db import transaction # type: ignore

# Configurar el entorno de Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehiculos_backend.settings')
django.setup()

from students.models import Estudiante

def limpiar_cadena(texto):
    """Función para limpiar y normalizar los textos"""
    return texto.strip().upper() if texto else ''

def cargar_estudiantes(archivo_csv):
    with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
        lector = csv.DictReader(csvfile)
        total = 0
        exitosos = 0
        errores = []
        
        with transaction.atomic():
            for fila in lector:
                total += 1
                try:
                    # Limpiar y normalizar datos
                    matricula = limpiar_cadena(fila['Matricula'])
                    apellido_paterno = limpiar_cadena(fila['Apellido Paterno'])
                    apellido_materno = limpiar_cadena(fila['Apellido Materno'])
                    nombre = limpiar_cadena(fila['Nombre'])
                    email = fila['Email'].strip().lower()

                    # Validaciones básicas
                    if not matricula:
                        raise ValueError("Matrícula vacía")
                    if not all(c.isalnum() for c in matricula):
                        raise ValueError("Matrícula contiene caracteres inválidos")
                    if not email or '@' not in email:
                        raise ValueError("Email inválido")

                    # Crear o actualizar estudiante
                    obj, created = Estudiante.objects.update_or_create(
                        matricula=matricula,
                        defaults={
                            'apellido_paterno': apellido_paterno,
                            'apellido_materno': apellido_materno,
                            'nombre': nombre,
                            'email': email
                        }
                    )
                    
                    exitosos += 1
                    if created:
                        print(f"Creado: {matricula}")
                    else:
                        print(f"Actualizado: {matricula}")

                except Exception as e:
                    errores.append({
                        'fila': total,
                        'matricula': matricula,
                        'error': str(e)
                    })
                    print(f"Error en fila {total}: {str(e)}")

        return {
            'total_registros': total,
            'exitosos': exitosos,
            'errores': errores
        }

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python cargar_estudiantes.py archivo.csv")
        sys.exit(1)
    
    archivo_csv = sys.argv[1]
    
    if not os.path.exists(archivo_csv):
        print(f"El archivo {archivo_csv} no existe")
        sys.exit(1)

    resultado = cargar_estudiantes(archivo_csv)
    
    print("\nResumen de carga:")
    print(f"Registros procesados: {resultado['total_registros']}")
    print(f"Registros exitosos: {resultado['exitosos']}")
    print(f"Errores: {len(resultado['errores'])}")
    
    if resultado['errores']:
        print("\nDetalle de errores:")
        for error in resultado['errores']:
            print(f"Fila {error['fila']} - Matrícula: {error['matricula']}")
            print(f"  Error: {error['error']}\n")