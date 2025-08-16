"""Modelo Partner: registro maestro de clientes facturables.

Descripción:
    Representa a las entidades (clientes finales) a las que se emiten
    planillas y facturas. El servicio puede ejecutarse para un tercero,
    pero en el sistema se referencia siempre al cliente final.

Notas:
    - Solo se registran clientes finales; intermediarios se gestionan fuera.
    - ``business_tax_id`` (RUC) es único y actúa como identificador fiscal.
    - Datos de contacto (email, phone, name_contact) son opcionales.
    - Hereda de ``BaseModel`` (timestamps, estado lógico, etc.).
    - Evitar duplicados validando RUC antes de crear.
"""

from django.db import models
from common.BaseModel import BaseModel


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
    address = models.CharField(
        'Dirección',
        max_length=255
    )
    name_contact = models.CharField(
        'Nombre de Contacto',
        max_length=255,
        blank=True,
        null=True
    )
    notes = models.TextField(
        'Notas',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Clientes'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.name
