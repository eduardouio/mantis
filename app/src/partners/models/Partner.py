from django.db import models
from common import BaseModel


# todos los socios de negocio son clientes
class Partner(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    code = models.CharField(
        'Código',
        max_length=50,
        unique=True
    )
    business_tax_id = models.CharField(
        'RUC',
        max_length=15,
        unique=True
    )
    partner = models.ManyToManyField(
        "self",
        blank=True,
    )
    name = models.CharField(
        'Nombre',
        max_length=255
    )
    address = models.CharField(
        'Dirección',
        max_length=255
    )
    city = models.CharField(
        'Ciudad',
        max_length=50
    )
    website = models.CharField(
        'Sitio Web',
        max_length=255,
        blank=True,
        null=True
    )
    phone = models.CharField(
        'Teléfono',
        max_length=20,
        blank=True,
        null=True
    )
    cargo_reference = models.CharField(
        'Referencia de Carga',
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self):
        if self.type_partner == 'client':
            return f'C: {self.name}'
        return f'S: {self.name}'
