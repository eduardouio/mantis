from django.db import models
from common.BaseModel import BaseModel


class CertificationVehicle(BaseModel):
    CERTIFICATION_NAME_CHOICES = (
        ('INSPECCION VOLUMETRICA', 'Inspección Volumétrica'),
        ('MEDICION DE ESPESORES', 'Medición de Espesores'),
        ('INSPECCION DE SEGURIDAD', 'Inspección de Seguridad'),
        ('PRUEBA HIDROSTATICA', 'Prueba Hidrostática'),
    )

    vehicle = models.ForeignKey(
        'equipment.Vehicle',
        on_delete=models.CASCADE,
        verbose_name='Vehículo',
        blank=True,
        null=True
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
