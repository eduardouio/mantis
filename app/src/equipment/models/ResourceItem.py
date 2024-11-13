from django.db import models
from common import BaseModel
from django.core.exceptions import ObjectDoesNotExist

TYPE_CHOISES = (
    ('EQUIPO', 'EQUIPO'),
    ('SERVICIO', 'SERVICIO')
)

STATUS_CHOICES = (
    ('DISPONIBLE', 'DISPONIBLE'),
    ('RENTADO', 'RENTADO'),
    ('DANADO', 'DANADO'),
    ('STAND BY', 'STAND BY'),
    ('EN REPARACION', 'EN REPARACION'),
    ('EN ALMACEN', 'EN ALMACEN')
)


class ResourceItem(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        'Nombre Equipo',
        max_length=255
    )
    type = models.CharField(
        'Tipo',
        max_length=255,
        choices=TYPE_CHOISES,
        default='EQUIPO'
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
    height = models.PositiveSmallIntegerField(
        'Altura',
        blank=True,
        null=True,
        default=None
    )
    width = models.PositiveSmallIntegerField(
        'Ancho',
        blank=True,
        null=True,
        default=None
    )
    depth = models.PositiveSmallIntegerField(
        'Profundidad',
        blank=True,
        null=True,
        default=None
    )
    weight = models.PositiveSmallIntegerField(
        'Peso',
        blank=True,
        null=True,
        default=None
    )
    status = models.CharField(
        'Estado',
        max_length=255,
        choices=STATUS_CHOICES,
        default='LIBRE'
    )
    # Estos campos se actualizan cada vez que el equipo cambia de proyecto
    # o de ubicación, no se actualiza manualmente
    # se libera cuando un proyecto termina, o libera el equipo
    bg_current_location = models.CharField(
        'Ubicación Actual',
        max_length=255,
        blank=True,
        null=True
    )
    bg_current_project = models.SmallIntegerField(
        'ID Proyecto Actual',
        blank=True,
        null=True
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

    @classmethod
    def get_equipment_by_id(cls, id_equipment):
        try:
            return ResourceItem.objects.get(id=id_equipment)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_free_equipment(cls):
        return cls.objects.filter(status='LIBRE').filter(is_active=True)

    def __str__(self):
        return self.name
