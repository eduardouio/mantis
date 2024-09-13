"""
    Modelos Personalizados de la Aplicación de Cuentas de Usuario.
    usamos el Correo Electrónico como nombre de usuario.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from accounts.managers import CustomUserManager


ROLE_CHOICES = (
    ('MANAGER', 'MANAGER'),
    ('TECNICO', 'TECNICO'),
)

POSITION_CHOICES = (
    ('Administrativo', 'Administrativo'),
    ('Tecnico', 'Tecnico'),
)


class CustomUserModel(AbstractUser):
    username = None
    email = models.EmailField(
        'correo electrónico',
        unique=True
    )
    dni = models.CharField(
        'Cédula',
        max_length=15
    )
    nro_phone = models.CharField(
        'Número de Celular',
        max_length=15
    )
    picture = models.ImageField(
        'imagen de perfil',
        upload_to='accounts/pictures',
        blank=True,
        help_text='Imagen de perfil del usuario.'
    )
    is_confirmed_mail = models.BooleanField(
        'correo electrónico confirmado',
        default=False,
        help_text='Estado de confirmación del correo electrónico.'
    )
    notes = models.TextField(
        'notas',
        blank=True
    )
    position = models.CharField(
        'cargo',
        max_length=255,
        choices=POSITION_CHOICES,
    )
    roles = models.CharField(
        'Role',
        choices=ROLE_CHOICES,
        default='sales',
        max_length=20
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    @classmethod
    def get(cls, email):
        try:
            return cls.objects.get(email=email)
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return self.email
