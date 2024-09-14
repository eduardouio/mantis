from djago.db import models
from common import BaseModel

CHOICES_TYPE_VEHICLE = (
    ('CAMION', 'CAMION'),
    ('VACCUM', 'VACCUM'),
    ('CAMIONETA', 'CAMIONETA'),
    ('AUTO', 'AUTO')
)

CHOICES_OWNER = (
    ('PEISOL', 'PEISOL'),
    ('COMPAÑIA CONTRATANANTE', 'CONTRATANANTE'),
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
        max_length=255,
        blank=True,
        null=True
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
    no_plate = models.CharField(
        'Placa',
        max_length=10,
        blank=True,
        null=True
    )
    owner_transport = models.CharField(
        'Propietario',
        max_length=255,
        choices=CHOICES_OWNER
    )

    def __str__(self):
        return '{}[{}]'.format(self.name, self.no_plate)
