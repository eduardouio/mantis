from django.db import models
from common import BaseModel

CHOICES_TYPE_VEHICLE = (
    ('CAMION', 'CAMION'),
    ('VACUUM', 'VACUUM'),
    ('CAMIONETA', 'CAMIONETA'),
    ('PLATAFORMA', 'PLATAFORMA'),
    ('AUTO', 'AUTO')
)

CHOICES_OWNER = (
    ('PEISOL', 'PEISOL'),
    ('CONTRATANANTE', 'CONTRATANANTE'),
)

CHOICES_STATUS_CERT = (
    ('VIGENTE', 'VIGENTE'),
    ('VENCIDO', 'VENCIDO'),
    ('NO APLICA', 'NO APLICA'),
    ('VENCIDO',  'VENCIDO'),
    ('POR VENCER', 'POR VENCER'),
    ('EN TRAMITE', 'EN TRAMITE'),
    ('RECHAZADO', 'RECHAZADO'),
)

CHOICES_STATUS_VEHICLES = (
    ('DISPONIBLE', 'DISPONIBLE'),
    ('EN MANTENIMIENTO', 'EN MANTENIMIENTO'),
    ('STANBY', 'STABY'),
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
    status_vehicle = models.CharField(
        'Estado Vehiculo',
        max_length=100,
        choices=CHOICES_STATUS_VEHICLES,
        default='DISPONIBLE'
    )
    status_cert_oper = (
        'Estado Certificado'
    )
    chasis = models.CharField(
        'Chasis',
        max_length=255,
        blank=True,
        null=True
    )
    motor_no = models.CharField(
        'No. Motor',
        max_length=255,
        blank=True,
        null=True
    )
    owner_transport = models.CharField(
        'Propietario',
        max_length=255,
        choices=CHOICES_OWNER,
        default='PEISOL'
    )
    due_date_matricula = models.DateField(
        'Vecimiento Matricula',
        blank=True,
        null=True,
        default=None
    )
    due_date_cert_oper = models.DateField(
        'Vecimiento Certificado de Operacion',
        blank=True,
        null=True,
        default=None
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
