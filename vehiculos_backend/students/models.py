from django.db import models
from django.core.validators import RegexValidator

class Estudiante(models.Model):
    matricula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Matrícula',
        validators=[
            RegexValidator(
                regex='^[A-Z0-9]+$',
                message='Formato inválido. Use mayúsculas y números'
            )
        ]
    )
    apellido_paterno = models.CharField(
        max_length=50,
        verbose_name='Apellido Paterno',
        validators=[
            RegexValidator(
                regex='^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$',
                message='Solo se permiten letras y espacios'
            )
        ]
    )
    apellido_materno = models.CharField(
        max_length=50,
        verbose_name='Apellido Materno',
        validators=[
            RegexValidator(
                regex='^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$',
                message='Solo se permiten letras y espacios'
            )
        ]
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre(s)',
        validators=[
            RegexValidator(
                regex='^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$',
                message='Solo se permiten letras y espacios'
            )
        ]
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Correo electrónico'
    )

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        ordering = ['apellido_paterno', 'apellido_materno', 'nombre']
        indexes = [
            models.Index(fields=['apellido_paterno', 'apellido_materno']),
            models.Index(fields=['matricula']),
        ]

    def __str__(self):
        return f"{self.matricula} - {self.nombre_completo}"

    @property
    def nombre_completo(self):
        return f"{self.apellido_paterno} {self.apellido_materno} {self.nombre}"