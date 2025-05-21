# Este script debe guardarse, por ejemplo, en:
# c:\Users\madma\Documents\ProyectoCalidad_Web_api\vehiculos_backend\students\create_student_users.py
# O puede ejecutarse directamente en la shell de Django.

import os
import django

# Configura Django si se ejecuta como script independiente
# Asegúrate de que la ruta a tu proyecto y settings esté correcta
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehiculos_backend.settings')
# django.setup()
# Las líneas anteriores son necesarias si ejecutas esto como un script standalone.
# Si lo ejecutas desde `manage.py shell`, no son necesarias.

from django.contrib.auth.models import User
from students.models import Estudiante # Asegúrate que la ruta al modelo Estudiante sea correcta
from django.db import transaction, IntegrityError
from django.core.exceptions import MultipleObjectsReturned

def create_users_for_students():
    """
    Crea usuarios de Django para estudiantes que aún no tienen uno vinculado.
    Usa el email del estudiante como username y email para el User.
    Usa la matrícula del estudiante como contraseña inicial.
    """
    students_without_users = Estudiante.objects.filter(user__isnull=True)
    created_count = 0
    linked_count = 0
    skipped_count = 0
    error_count = 0

    print(f"Procesando {students_without_users.count()} estudiantes sin usuario vinculado...")

    for student in students_without_users:
        if not student.email or not student.matricula:
            print(f"SALTANDO: Estudiante ID {student.id} (Matrícula: {student.matricula}) - Email o matrícula faltante.")
            skipped_count += 1
            continue

        try:
            with transaction.atomic():
                # Intentar encontrar un usuario existente por email
                try:
                    existing_user = User.objects.get(email=student.email)
                    student.user = existing_user
                    student.save()
                    print(f"VINCULADO: Usuario existente {existing_user.username} vinculado a estudiante {student.matricula} ({student.email}).")
                    linked_count += 1
                    continue # Siguiente estudiante
                except User.DoesNotExist:
                    # El usuario no existe por email, se procederá a crear uno nuevo
                    pass
                except MultipleObjectsReturned:
                    print(f"ERROR: Múltiples usuarios encontrados con email {student.email}. No se puede vincular automáticamente al estudiante {student.matricula}. Por favor, revise manualmente.")
                    error_count += 1
                    continue # Siguiente estudiante

                # Crear un nuevo usuario
                # Usar email como username. Si ya existe, intentar con matrícula.
                username_to_try = student.email
                if User.objects.filter(username=username_to_try).exists():
                    username_to_try = student.matricula # Intento alternativo de username
                    if User.objects.filter(username=username_to_try).exists():
                        print(f"SALTANDO: Estudiante {student.matricula} ({student.email}) - Username '{student.email}' y '{student.matricula}' ya existen.")
                        skipped_count += 1
                        continue # Siguiente estudiante
                
                new_user = User()
                new_user.username = username_to_try
                new_user.email = student.email
                new_user.set_password(student.matricula) # Esto cifra la contraseña
                
                new_user.first_name = student.nombre if student.nombre else ''
                
                last_name_parts = []
                if student.apellido_paterno:
                    last_name_parts.append(student.apellido_paterno)
                if student.apellido_materno:
                    last_name_parts.append(student.apellido_materno)
                new_user.last_name = " ".join(last_name_parts).strip()
                
                new_user.is_active = True
                new_user.is_staff = False
                
                new_user.save()

                student.user = new_user
                student.save()
                
                print(f"CREADO: Usuario {new_user.username} para estudiante {student.matricula} ({student.email}).")
                created_count += 1

        except IntegrityError as e:
            print(f"ERROR de Integridad procesando estudiante {student.matricula} ({student.email}): {e}. Podría ser un username duplicado si el email no es único en auth_user.username.")
            error_count += 1
        except Exception as e:
            print(f"ERROR INESPERADO procesando estudiante {student.matricula} ({student.email}): {e}")
            error_count += 1

    print("\n--- Resumen ---")
    print(f"Usuarios nuevos creados y vinculados: {created_count}")
    print(f"Usuarios existentes vinculados: {linked_count}")
    print(f"Estudiantes saltados (datos faltantes o usernames duplicados): {skipped_count}")
    print(f"Errores: {error_count}")
    print("Proceso completado.")

# Para ejecutar esta función:
# 1. Asegúrate de estar en el directorio raíz de tu proyecto Django (donde está manage.py).
#    En tu caso: C:\Users\madma\Documents\ProyectoCalidad_Web_api\vehiculos_backend
# 2. Abre la shell de Django:
#    python manage.py shell
# 3. Una vez en la shell, importa la función. Si guardaste el script como se sugirió:
#    from students.create_student_users import create_users_for_students
#    (Si pegas el código directamente en la shell, no necesitas el import)
# 4. Ejecuta la función:
#    create_users_for_students()