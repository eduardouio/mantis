from django.db import models
from common import BaseModel


CHOICES_CODE = (
    ('PSL-BT-FP', 'PSL-BT-FP'),
    ('PSL-BT-TPL', 'PSL-BT-TPL'),
    ('PSL-LV-PJ', 'PSL-LV-PJ'),
    ('PSL-UO-TPL', 'PSL-UO-TPL'),
    ('PSL-AR', 'PSL-AR'),
    ('PSL-AP', 'PSL-AP'),
    ('PSL-TA', 'PSL-TA')
)
STATUS_CHOICES = (
    ('DISPONIBLE', 'DISPONIBLE'),
    ('DANADO', 'DANADO'),
    ('STAND BY', 'STAND BY'),
    ('EN REPARACION', 'EN REPARACION'),
    ('EN RENTA', 'EN RENTA'),
    ('EN ALMACEN', 'EN ALMACEN')
)


class Equipment(BaseModel):
    id = models.AutoField(
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
        null=True,
        default='N/A'
    )
    code = models.CharField(
        'Código Equipo',
        max_length=50,
        unique=True
    )
    date_purchase = models.DateField(
        'Fecha de Compra',
        blank=True,
        null=True,
        default=None
    )
    height = models.DecimalField(
        'Altura',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        default=None
    )
    width = models.DecimalField(
        'Ancho',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        default=None
    )
    depth = models.DecimalField(
        'Profundidad',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        default=None
    )
    weight = models.DecimalField(
        'Peso',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        default=None
    )
    description = models.CharField(
        'Descripción',
        max_length=255,
        blank=True,
        null=True,
        default=None
    )
    status = models.CharField(
        'Estado',
        max_length=255,
        choices=STATUS_CHOICES,
        default='OPERATIVO'
    )
    is_active = models.BooleanField(
        'Activo?',
        default=True
    )
    # Estos campos se actualizan cada vez que el equipo cambia de proyecto
    # o de ubicación, no se actualiza manualmente
    # se libera cuando un proyecto termina, o libera el equipo
    bg_current_location = models.CharField(
        'Ubicación Actual',
        max_length=255
    )
    bg_current_project = models.CharField(
        'Proyecto Actual',
        max_length=255
    )
    bg_date_commitment = models.DateField(
        'Fecha de Compromiso',
        blank=True,
        null=True
    )
    bg_date_free = models.DateField(
        'Fecha de Liberación',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name
