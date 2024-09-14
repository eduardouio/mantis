from django.db import models
from .Mantenance import Mantenance
from common import BaseModel
from equipment.models import Vehicle


class ChainOfCustody(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    mantenance = models.ForeignKey(
        Mantenance,
        on_delete=models.CASCADE
    )
    date = models.DateField(
        'Fecha'
    )
    origin_location = models.CharField(
        'Ubicación de Origen',
        max_length=255
    )
    destination_location = models.CharField(
        'Ubicación de Dispocisión Final',
        max_length=255
    )
    volume = models.CharField(
        'Volumen',
        max_length=255
    )
    responsible = models.CharField(
        'Responsable',
        max_length=255
    )
    vehicle = models.ForeignKey(
        'equipment.Vehicle',
        on_delete=models.RESTRICT
    )
    observation = models.TextField(
        'Observaciones'
    )
    nro_dni = models.CharField(
        'Nro. Cedula',
        max_length=8
    )
    type_license = models.CharField(
        'Tipo de Licencia',
        max_length=10
    )
    check_by = models.CharField(
        'Revisado por',
        max_length=255
    )


ACCION_CHOICES = (
    ('ENVIO', 'ENVIO'),
    ('TRANSPORTE', 'TRANSPORTE'),
    ('RECIBE', 'RECIBE'),
)


class ChainOfCustodyPersonal(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    chain_of_custody = models.ForeignKey(
        ChainOfCustody,
        on_delete=models.CASCADE
    )
    date = models.DateField(
        'Fecha'
    )
    name = models.CharField(
        'Nombre del Personal',
        max_length=255
    )
    nro_dni = models.CharField(
        'Nro. DNI',
        max_length=15
    )
    position = models.CharField(
        'Cargo',
        max_length=255,
        blank=True,
        null=True
    )
    accion = models.CharField(
        'Acción',
        max_length=255,
        choices=ACCION_CHOICES
    )
