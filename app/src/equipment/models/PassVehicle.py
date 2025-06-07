from django.db import models
from common.BaseModel import BaseModel


class PassVehicle(BaseModel):
    vehicle = models.ForeignKey(
        'equipment.Vehicle',
        on_delete=models.CASCADE,
        verbose_name='Vehículo'
    )
    BLOQUE_CHOICES = [
        ('petroecuador', 'Tarjeta de Petroecuador'),
        ('shaya', 'Shaya'),
        ('consorcio_shushufindi', 'Consorcio Shushufindi'),
        ('enap_sipec', 'ENAP SIPEC'),
        ('orion', 'Tarjeta Orion'),
        ('andes_petroleum', 'Andes Petroleum'),
        ('pardalis_services', 'Pardalis Services'),
        ('frontera_energy', 'Frontera Energy'),
        ('gran_tierra', 'Gran Tierra'),
        ('pcr', 'PCR'),
        ('halliburton', 'Halliburton'),
        ('gente_oil', 'Gente Oil'),
        ('tribiol_gas', 'Tribiol Gas'),
        ('adico', 'Adico'),
        ('cuyaveno_petro', 'Cuyaveno Petro'),
        ('geopark', 'Geopark'),
    ]
    bloque = models.CharField(
        max_length=32,
        choices=BLOQUE_CHOICES,
        verbose_name='Nombre de Bloque'
    )
    fecha_caducidad = models.DateField(
        verbose_name='Fecha de caducidad'
    )

    @classmethod
    def get_by_vehicle(cls, vehicle_id):
        """
        Obtiene los registros de pases de un vehículo específico.
        """
        return cls.objects.filter(vehicle_id=vehicle_id, is_active=True)

    def __str__(self):
        return f'{self.vehicle} - {self.bloque}'
