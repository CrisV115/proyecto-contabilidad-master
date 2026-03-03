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
    PAGO_DECIMO_CHOICES = [
        ('mensual', 'Mensualizado'),
        ('anual', 'Acumulado anual'),
    ]

    apellidos_nombres = models.CharField(max_length=200)
    cedula_pasaporte = models.CharField(max_length=20, unique=True)
    cargo = models.CharField(max_length=120)
    fecha_ingreso = models.DateField()
    sueldo = models.DecimalField(max_digits=10, decimal_places=2)
    preferencia_decimo_tercero = models.CharField(
        max_length=10,
        choices=PAGO_DECIMO_CHOICES,
        default='mensual'
    )
    preferencia_decimo_cuarto = models.CharField(
        max_length=10,
        choices=PAGO_DECIMO_CHOICES,
        default='mensual'
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.apellidos_nombres} - {self.cedula_pasaporte}"


class NominaMensual(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='nominas')
    periodo = models.DateField(help_text='Representa el primer día del mes liquidado.')

    horas_suplementarias = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    horas_extraordinarias = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    bonificaciones_comisiones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sbu = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    valor_horas_suplementarias = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_horas_extraordinarias = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ingresos_gravables = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    aporte_iess_personal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    decimo_tercero_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    decimo_tercero_acumulado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    decimo_cuarto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    decimo_cuarto_acumulado = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fondos_reserva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_egresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    liquido_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-periodo', 'empleado__apellidos_nombres']
        constraints = [
            models.UniqueConstraint(fields=['empleado', 'periodo'], name='unique_nomina_empleado_periodo')
        ]

    def __str__(self):
        return f"{self.empleado.apellidos_nombres} - {self.periodo:%m/%Y}"
