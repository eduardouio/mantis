from django import models
from accounts.models import Technical
from common.models import BaseModel


class PassTechnical(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    technical = models.OneToOneField(Technical, on_delete=models.CASCADE)
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
