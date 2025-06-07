from django.db import models
from common.BaseModel import BaseModel

CERTIFICATION_NAME_CHOICES = (
    ('INSPECCION_VOLUMETRICA', 'Inspección Volumétrica'),
    ('MEDICION_DE_ESPESORES', 'Medición de Espesores'),
    ('INSPECCION_DE_SEGURIDAD', 'Inspección de Seguridad'),
    ('PRUEBA_HIDROSTATICA', 'Prueba Hidrostática'),
)


class CertificationVehicle(BaseModel):
    vehicle = models.ForeignKey(
        'equipment.Vehicle',
        on_delete=models.CASCADE,
        verbose_name='Vehículo'
    )
    name = models.CharField(
        'Nombre de Certificación',
        max_length=50,
        choices=CERTIFICATION_NAME_CHOICES
    )
    date_start = models.DateField(
        'Fecha de Inicio'
    )
    date_end = models.DateField(
        'Fecha de Fin'
    )
    description = models.TextField(
        'Descripción',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.get_name_display()} - {self.vehicle.no_plate if self.vehicle else "Sin Vehículo"}'