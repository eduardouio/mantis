from django.db import models
from common import BaseModel

CERTIFICATION_NAME_CHOICES = (
    ('INSPECCION_VOLUMETRICA', 'Inspección Volumétrica'),
    ('MEDICION_DE_ESPESORES', 'Medición de Espesores'),
    ('INSPECCION_DE_SEGURIDAD', 'Inspección de Seguridad'),
    ('PRUEBA_HIDROSTATICA', 'Prueba Hidrostática'),
)


class CertificationVehicle(BaseModel):
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

    def __str__(self):
        return f'{self.get_name_display()} - {self.no_plate}'