from django.db import models

class Vehiculo(models.Model):
    matricula = models.CharField(max_length=20, unique=True)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    modelo_vehiculo = models.CharField(max_length=100)
    placa = models.CharField(max_length=15)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.matricula} - {self.nombre}"