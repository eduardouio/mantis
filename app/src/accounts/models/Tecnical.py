from django.db import models
from common import BaseModel
from accounts.models import CustomUserModel


POSITION_CHOICES = (
    ('Administrativo', 'Administrativo'),
    ('Tecnico', 'Tecnico'),
)


class Technical(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    first_name = models.CharField(
        'Nombres',
        max_length=255
    )
    last_name = models.CharField(
        'Apellidos',
        max_length=255
    )
    dni = models.CharField(
        'Cédula',
        max_length=15
    )
    user = models.OneToOneField(
        CustomUserModel,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None
    )
    nro_phone = models.CharField(
        'Número de Celular',
        max_length=15
    )
    position = models.CharField(
        'cargo',
        max_length=255,
        choices=POSITION_CHOICES,
    )
    days_to_work = models.PositiveSmallIntegerField(
        'días a trabajar',
        default=22,
        help_text='Días a trabajar por mes'
    )
    days_free = models.PositiveSmallIntegerField(
        'días libres',
        default=8,
        help_text='Días libres por mes'
    )