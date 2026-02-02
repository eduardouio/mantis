from django.db import models
from accounts.models import Technical
from common.BaseModel import BaseModel


class PassTechnical(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    technical = models.ForeignKey(Technical, on_delete=models.CASCADE)
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
        verbose_name='Fecha de caducidad',
        blank=True,
        null=True
    )
    pass_file = models.FileField(
        upload_to='pass_technicals/',
        verbose_name='Archivo de pase',
        blank=True,
        null=True
    )

    @classmethod
    def get_by_technical(cls, technical_id):
        """
        Obtiene el registro de pase de un técnico específico.
        Si no existe, retorna None.
        """
        try:
            return cls.objects.get(technical_id=technical_id)
        except cls.DoesNotExist:
            return None
