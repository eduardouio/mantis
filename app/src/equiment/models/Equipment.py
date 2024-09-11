from django.db import models
from common import BaseModel


class Equipment(BaseModel):
    id_equipment = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        'Nombre Equipo',
        max_length=255
    )
    brand = models.CharField(
        'Marca',
        max_length=255,
        default='SIN MARCA'
    )
    model = models.CharField(
        'Modelo',
        max_length=255,
        blank=True,
        null=True
    )
    date_purchase = models.DateField(
        'Fecha de Compra'
    )
    id_code = models.CharField(
        'Identificaor de Equipo',
        max_length=255,
        unique=True
    )
    height = models.DecimalField(
        'Altura',
        max_digits=5,
        decimal_places=2
    )
    width = models.DecimalField(
        'Ancho',
        max_digits=5,
        decimal_places=2
    )
    weight = models.DecimalField(
        'Peso',
        max_digits=5,
        decimal_places=2
    )
    depth = models.DecimalField(
        'Profundidad',
        max_digits=5,
        decimal_places=2
    )
    description = models.TextField(
        'Descripción',
        blank=True,
        null=True
    )
    is_available = models.BooleanField(
        'Disponible',
        default=True
    )
    current_location = models.CharField(
        'Ubicación Actual',
        max_length=255
    )
    current_project = models.CharField(
        'Proyecto Actual',
        max_length=255
    )
    date_commitment = models.DateField(
        'Fecha de Compromiso',
        blank=True,
        null=True
    )
    date_free = models.DateField(
        'Fecha de Liberación',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name
