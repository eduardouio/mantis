from django.db import models
from accounts.models import CustomUserModel
from django.utils import timezone
from datetime import timedelta
from common import BaseModel


class License(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    user = models.OneToOneField(
        CustomUserModel,
        on_delete=models.CASCADE
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

    def activate(self):
        """ Activa la licencia y asigna fechas de expiración """
        self.is_active = True
        self.activated_on = timezone.now()
        self.expires_on = timezone.now() + timedelta(days=365)
        self.save()

    def __str__(self):
        return f"Licencia de {self.user.username} - Activa: {self.is_active}"
