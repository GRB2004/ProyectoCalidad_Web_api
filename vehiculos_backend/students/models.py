from django.db import models
from django.dispatch import receiver
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings

class BearerTokenAuthentication(TokenAuthentication):
    keyword = u"Bearer"


class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # <--- Agrega esto
    matricula = models.CharField(max_length=255,null=True, blank=True)
    apellido_paterno = models.CharField(max_length=255,null=True, blank=True)
    apellido_materno = models.CharField(max_length=255,null=True, blank=True)
    nombre = models.CharField(max_length=255,null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del alumno "+self.email+" "+self.nombre+" "+self.apellido_paterno+" "+self.apellido_materno
    
class Entrada(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='entradas')
    placas = models.CharField(max_length=255, null=True, blank=True)
    entrada = models.CharField(max_length=255, null=True, blank=True)
    acciones = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Entrada de vehículo - Placa: {self.placas} - Estudiante: {self.estudiante.matricula}"