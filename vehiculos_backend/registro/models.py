from django.db import models
from django.utils import timezone

class RegistroActivo(models.Model):
    placa = models.CharField(max_length=15)
    estudiante_matricula = models.CharField(max_length=20)
    entry_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Registro Activo"
        verbose_name_plural = "Registros Activos"

class RegistroHistorial(models.Model):
    placa = models.CharField(max_length=15)
    estudiante_matricula = models.CharField(max_length=20)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField()
    duration = models.DurationField()
    
    class Meta:
        verbose_name = "Registro Histórico"
        verbose_name_plural = "Registros Históricos"

    def save(self, *args, **kwargs):
        if self.exit_time and self.entry_time:
            self.duration = self.exit_time - self.entry_time
        super().save(*args, **kwargs)