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
        max_length=255,
        blank=True,
        null=True,
        default=None
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
        on_delete=models.PROTECT,
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

    @classmethod
    def get_true_false_list(cls, partner):
        registered_techs_id = set(
            tech.id for tech in partner.authorized_tehcnicals.all()
        )
        true_false_techs = [
            {
                'id': tech.id,
                'first_name': tech.first_name,
                'last_name': tech.last_name,
                'role': tech.role,
                'is_registered': tech.id in registered_techs_id

            }
            for tech in cls.objects.all()
        ]

        return true_false_techs

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'
