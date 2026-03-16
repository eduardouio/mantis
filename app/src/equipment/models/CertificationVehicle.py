from django.db import models
from common.BaseModel import BaseModel
from common.validators import validate_pdf_file


class CertificationVehicle(BaseModel):
    vehicle = models.ForeignKey(
        'equipment.Vehicle',
        on_delete=models.CASCADE,
        verbose_name='Vehículo',
        blank=True,
        null=True
    )
    name = models.CharField(
        'Nombre de Certificación',
        max_length=100
    )
    date_start = models.DateField(
        'Fecha de Inicio'
    )
    date_end = models.DateField(
        'Fecha de Fin',
        blank=True,
        null=True
    )
    description = models.TextField(
        'Descripción',
        blank=True,
        null=True
    )
    certification_file = models.FileField(
        upload_to='vehicles/certifications/',
        verbose_name='Archivo de Certificación',
        validators=[validate_pdf_file],
        blank=True,
        null=True
    )

    @classmethod
    def get_unique_names(cls):
        """Retorna los valores únicos de nombre de certificación registrados en la base de datos."""
        return list(
            cls.objects.filter(is_active=True)
            .exclude(name__isnull=True)
            .exclude(name__exact='')
            .values_list('name', flat=True)
            .distinct()
            .order_by('name')
        )

    def __str__(self):
        return f'{self.name} - {self.vehicle.no_plate if self.vehicle else "Sin Vehículo"}'
