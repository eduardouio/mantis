from django.db import models
from common import BaseModel
from accounts.models import CustomUserModel

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
    licence_file = models.CharField(
        'Licencia',
        max_length=250,
        null=True,
        blank=True
    )
    role = models.CharField(
        'Role',
        choices=ROLE_CHOICES,
        default='USER',
        max_length=20
    )
    enterprise = models.CharField(
        'Empresa',
        max_length=50,
        default='PEISOL S.A.'
    )
    is_active = models.BooleanField(
        'Activo?',
        default=False
    )
    url_server = models.URLField(
        'URL del servidor',
        null=True,
        blank=True,
        default='https://dev-7.com/licenses/'
    )
    user = models.ForeignKey(
        CustomUserModel,
        on_delete=models.PROTECT
    )
