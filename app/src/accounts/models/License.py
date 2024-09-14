from django.db import models
from common import BaseModel
from accounts.models.CustomUserModel import CustomUserModel

ROLE_CHOICES = (
    ('ADMINISTRATIVO', 'ADMINISTRATIVO'),
    ('TECNICO', 'TECNICO'),
)


class License(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    license_key = models.CharField(
        'clave de licencia',
        max_length=100, unique=True
    )
    activated_on = models.DateTimeField(
        'activada el',
        null=True,
        blank=True
    )
    expires_on = models.DateTimeField(
        'expira el',
        null=True,
        blank=True
    )
    licence_file = models.TextField(
        'Contenido de Licencia',
        null=True,
        blank=True
    )
    role = models.CharField(
        'Role',
        choices=ROLE_CHOICES,
        default='TECNICO',
        max_length=20
    )
    is_active = models.BooleanField(
        'Activo?',
        default=False
    )
    user = models.ForeignKey(
        CustomUserModel,
        on_delete=models.CASCADE
    )
