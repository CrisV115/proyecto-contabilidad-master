from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):

    telefono = models.CharField(max_length=10)

    PREGUNTAS = [
        ('mascota', '¿Cómo se llama tu primera mascota?'),
        ('madre', '¿Cuál es el segundo nombre de tu madre?'),
        ('ciudad', '¿En qué ciudad naciste?'),
    ]

    pregunta_seguridad = models.CharField(max_length=50, choices=PREGUNTAS)
    respuesta_seguridad = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Empleado(models.Model):
    apellidos_nombres = models.CharField(max_length=200)
    cedula_pasaporte = models.CharField(max_length=20, unique=True)
    cargo = models.CharField(max_length=120)
    fecha_ingreso = models.DateField()
    sueldo = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.apellidos_nombres} - {self.cedula_pasaporte}"
