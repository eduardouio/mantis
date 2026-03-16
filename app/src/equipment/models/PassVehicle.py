from django.db import models
from common.BaseModel import BaseModel
from common.validators import validate_pdf_file


class PassVehicle(BaseModel):
    vehicle = models.ForeignKey(
        'equipment.Vehicle',
        on_delete=models.CASCADE,
        verbose_name='Vehículo'
    )
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
        upload_to='vehicles/passes/',
        verbose_name='Archivo de pase',
        validators=[validate_pdf_file],
        blank=True,
        null=True
    )
    @classmethod
    def get_by_vehicle(cls, vehicle_id):
        """
        Obtiene los registros de pases de un vehículo específico.
        """
        return cls.objects.filter(vehicle_id=vehicle_id, is_active=True)

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

    def __str__(self):
        return f'{self.vehicle} - {self.bloque}'
