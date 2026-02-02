from django.db import models
from common.BaseModel import BaseModel


class PassVehicle(BaseModel):
    vehicle = models.ForeignKey(
        'equipment.Vehicle',
        on_delete=models.CASCADE,
        verbose_name='Vehículo'
    )
    BLOQUE_CHOICES = [
        ('PETROECUADOR', 'PETROECUADOR'),
        ('SHAYA', 'SHAYA'),
        ('CONSORCIO SHUSHUFINDI', 'CONSORCIO SHUSHUFINDI'),
        ('ENAP SIPEC', 'ENAP SIPEC'),
        ('ORION', 'ORION'),
        ('ANDES PETROLEUM', 'ANDES PETROLEUM'),
        ('PARDALIS SERVICES', 'PARDALIS SERVICES'),
        ('FRONTERA ENERGY', 'FRONTERA ENERGY'),
        ('GRAN TIERRA', 'GRAN TIERRA'),
        ('PCR', 'PCR'),
        ('HALLIBURTON', 'HALLIBURTON'),
        ('GENTE OIL', 'GENTE OIL'),
        ('TRIBIOL GAS', 'TRIBIOL GAS'),
        ('ADICO', 'ADICO'),
        ('CUYAVENO PETRO', 'CUYAVENO PETRO'),
        ('GEOPARK', 'GEOPARK'),
    ]
    bloque = models.CharField(
        max_length=32,
        choices=BLOQUE_CHOICES,
        verbose_name='Nombre de Bloque'
    )
    fecha_caducidad = models.DateField(
        verbose_name='Fecha de caducidad',
        blank=True,
        null=True
    )
    pass_file = models.FileField(
        upload_to='pass_vehicles/',
        verbose_name='Archivo de pase',
        blank=True,
        null=True
    )
    @classmethod
    def get_by_vehicle(cls, vehicle_id):
        """
        Obtiene los registros de pases de un vehículo específico.
        """
        return cls.objects.filter(vehicle_id=vehicle_id, is_active=True)

    def __str__(self):
        return f'{self.vehicle} - {self.bloque}'
