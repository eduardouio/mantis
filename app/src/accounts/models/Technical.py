from django.db import models
from common import BaseModel
from accounts.models.CustomUserModel import CustomUserModel


ROLE_CHOICES = (
    ('ADMINISTRATIVO', 'ADMINISTRATIVO'),
    ('TECNICO', 'TECNICO'),
)
LOCATION_CHOICES = (
    ('CAMPO BASE', 'CAMPO BASE'),
    ('CHANANHUE', 'CHANANHUE'),
    ('CPP', 'CPP'),
)


class Technical(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    date_joined = models.DateField(
        'Fecha de Ingreso',
        blank=True,
        null=True,
        default=None
    )
    first_name = models.CharField(
        'Nombres',
        max_length=255
    )
    last_name = models.CharField(
        'Apellidos',
        max_length=255
    )
    email = models.EmailField(
        'Correo Electrónico',
        unique=True,
    )
    location = models.CharField(
        'Ubicación',
        max_length=255,
        choices=LOCATION_CHOICES,
        default='CAMPO BASE'
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
    role = models.CharField(
        'cargo',
        max_length=255,
        choices=ROLE_CHOICES,
    )
    days_to_work = models.PositiveSmallIntegerField(
        'días a trabajar',
        default=22,
        help_text='Días a trabajar por mes'
    )
    days_free = models.PositiveSmallIntegerField(
        'días libres',
        default=7,
        help_text='Días libres por mes'
    )
    is_active = models.BooleanField(
        'Activo?',
        default=False
    )

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'