from django.db import models
from common import BaseModel

CHOICES_TYPE_VEHICLE = (
    ('CAMION', 'CAMION'),
    ('VACUUM', 'VACUUM'),
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
    type_vehicle = models.CharField(
        'Tipo de Vehículo',
        max_length=255,
        choices=CHOICES_TYPE_VEHICLE
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

    @classmethod
    def get_true_false_list(cls, partner):
        registered_vehicles_id = set(
            vehicle.id for vehicle in partner.authorized_vehicle.all()
        )

        true_or_false_vehicles = [
            {
                'id': vehicle.id,
                'no_plate': vehicle.no_plate,
                'type_vehicle': vehicle.type_vehicle,
                'is_registered': vehicle.id in registered_vehicles_id
            }
            for vehicle in cls.objects.all()
        ]

        return true_or_false_vehicles

    def __str__(self):
        return self.no_plate
