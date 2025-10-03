from django.db import models
from common.BaseModel import BaseModel

CHOICES_TYPE_VEHICLE = (
    ('CAMION', 'CAMION'),
    ('VACUUM', 'VACUUM'),
    ('CAMIONETA', 'CAMIONETA'),
    ('PLATAFORMA', 'PLATAFORMA'),
    ('AUTO', 'AUTO')
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
    status_cert_oper = models.CharField(
        'Estado Certificado',
        max_length=100,
        choices=CHOICES_STATUS_CERT,
        default='VIGENTE',
        blank=True,
        null=True
    )
    chasis = models.CharField(
        'Chasis',
        max_length=255,
        blank=True,
        null=True
    )
    color = models.CharField(
        'Color',
        max_length=255,
        blank=True,
        null=True
    )
    owner_transport = models.CharField(
        'Propietario',
        max_length=255,
        default='PEISOL'
    )
    date_cert_oper = models.DateField(
        'Fecha Certificado de Operacion',
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
    date_matricula = models.DateField(
        'Fecha Matricula',
        blank=True,
        null=True,
        default=None
    )
    due_date_matricula = models.DateField(
        'Vecimiento Matricula',
        blank=True,
        null=True,
        default=None
    )
    date_mtop = models.DateField(
        'Fecha MTOP',
        blank=True,
        null=True,
        default=None
    )
    due_date_mtop = models.DateField(
        'Fecha Vencimiento MTOP',
        blank=True,
        null=True,
        default=None
    )
    date_technical_review = models.DateField(
        'Fecha Revisión Técnica',
        blank=True,
        null=True,
        default=None
    )
    due_date_technical_review = models.DateField(
        'Fecha Vencimiento Revisión Técnica',
        blank=True,
        null=True,
        default=None
    )
    nro_poliza = models.CharField(
        'Número de Póliza',
        max_length=255,
        blank=True,
        null=True
    )
    insurance_company = models.CharField(
        'Compañía de Seguros',
        max_length=255,
        blank=True,
        null=True
    )
    insurance_expiration_date = models.DateField(
        'Fecha Vencimiento Póliza',
        blank=True,
        null=True,
        default=None
    )
    insurance_issue_date = models.DateField(
        'Fecha Emisión Póliza',
        blank=True,
        null=True,
        default=None
    )
    duedate_satellite = models.DateField(
        'Fecha Vencimiento Satelital',
        blank=True,
        null=True,
        default=None
    )
    serial_number = models.CharField(
        'Número de Serie',
        max_length=255,
        blank=True,
        null=True
    )
    engine_number = models.CharField(
        'Número de Motor',
        max_length=255,
        blank=True,
        null=True
    )
    chassis_number = models.CharField(
        'Número de Chasis',
        max_length=255,
        blank=True,
        null=True
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
