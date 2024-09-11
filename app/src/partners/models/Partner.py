from django.db import models
from common import BaseModel


# todos los socios de negocio son clientes
class Partner(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    business_tax_id = models.CharField(
        'RUC',
        max_length=15,
        unique=True
    )
    name = models.CharField(
        'Nombre',
        max_length=255
    )
    email = models.EmailField(
        'Correo Electrónico',
        max_length=255
    )
    phone = models.CharField(
        'Teléfono',
        max_length=20
    )
    name_contact = models.CharField(
        'Nombre de Contacto',
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name
