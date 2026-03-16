from django.db import models
from accounts.models import Technical
from common.BaseModel import BaseModel
from common.validators import validate_pdf_file


class PassTechnical(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    technical = models.ForeignKey(Technical, on_delete=models.CASCADE)
    bloque = models.CharField(
        max_length=100,
        verbose_name='Nombre de Bloque'
    )
    fecha_caducidad = models.DateField(
        verbose_name='Fecha de caducidad',
        blank=True,
        null=True
    )
    pass_file = models.FileField(
        upload_to='technicals/passes/',
        verbose_name='Archivo de pase',
        validators=[validate_pdf_file],
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

    @classmethod
    def get_unique_bloques(cls):
        """Retorna los valores únicos de bloque registrados en la base de datos."""
        return list(
            cls.objects.filter(is_active=True)
            .exclude(bloque__isnull=True)
            .exclude(bloque__exact='')
            .values_list('bloque', flat=True)
            .distinct()
            .order_by('bloque')
        )
