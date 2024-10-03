from django.db import models
from common import BaseModel

CHOICES_TYPE_VEHICLE = (
    ('CAMION', 'CAMION'),
    ('VACCUM', 'VACCUM'),
    ('CAMIONETA', 'CAMIONETA'),
    ('AUTO', 'AUTO')
)

CHOICES_OWNER = (
    ('PEISOL', 'PEISOL'),
    ('CONTRATANANTE', 'CONTRATANANTE'),
)


class Vehicle(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        'Nombre',
        max_length=255
    )
    brand = models.CharField(
        'Marca',
        max_length=255,
        default='SIN MARCA'
    )
    code_vehicle = models.CharField(
        'Código de Vehículo',
        max_length=100,
        unique=True
    )
    model = models.CharField(
        'Modelo',
        max_length=255,
        blank=True,
        null=True
    )
    type_vehicle = models.CharField(
        'Tipo de Vehículo',
        max_length=255
    )
    year = models.IntegerField(
        'Año',
        blank=True,
        null=True
    )
    no_plate = models.CharField(
        'Placa',
        max_length=10,
        unique=True
    )
    owner_transport = models.CharField(
        'Propietario',
        max_length=255,
        choices=CHOICES_OWNER,
        default='PEISOL'
    )
    is_active = models.BooleanField(
        'Activo?',
        default=True
    )

    def __str__(self):
        return self.no_plate
