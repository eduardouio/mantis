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
    ('OPERATIVO', 'OPERATIVO'),
    ('DANADO', 'DANADO'),
    ('EN REPARACIÓN', 'EN REPARACIÓN'),
)


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
    code = models.CharField(
        'Código',
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
    status = models.CharField(
        'Estado',
        max_length=255,
        choices=STATUS_CHOICES,
        default='OPERATIVO'
    )
    # Estos campos se actualizan cada vez que el equipo cambia de proyecto
    # o de ubicación, no se actualiza manualmente
    # se libera cuando un proyecto termina, o libera el equipo
    _current_location = models.CharField(
        'Ubicación Actual',
        max_length=255
    )
    _current_project = models.CharField(
        'Proyecto Actual',
        max_length=255
    )
    _date_commitment = models.DateField(
        'Fecha de Compromiso',
        blank=True,
        null=True
    )
    _date_free = models.DateField(
        'Fecha de Liberación',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name
