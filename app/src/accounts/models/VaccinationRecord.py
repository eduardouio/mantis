from django.db import models
from common.BaseModel import BaseModel
from .Technical import Technical


class VaccinationRecord(BaseModel):
    VACCINE_TYPE_CHOICES = (
        ('HEPATITIS_A_B', 'Hepatitis A y B'),
        ('TETANUS', 'Tétanos'),
        ('TYPHOID', 'Tifoidea'),
        ('YELLOW_FEVER', 'Fiebre Amarilla'),
        ('INFLUENZA', 'Influenza'),
        ('MEASLES', 'Sarampión'),
        ('COVID', 'Covid-19'),
        ('OTHER', 'Otra'),
    )
    id = models.AutoField(
        primary_key=True
    )
    technical = models.ForeignKey(
        Technical,
        on_delete=models.CASCADE,
        related_name='vaccination_records',
        verbose_name='Técnico'
    )
    vaccine_type = models.CharField(
        'Tipo de Vacuna',
        max_length=50,
        choices=VACCINE_TYPE_CHOICES
    )
    batch_number = models.CharField(
        'Número de Lote',
        max_length=50,
        blank=True,
        null=True,
        help_text='Número de lote de la vacuna administrada.'
    )
    application_date = models.DateField(
        'Fecha de Aplicación'
    )
    dose_number = models.PositiveSmallIntegerField(
        'Número de Dosis',
        blank=True,
        null=True,
        help_text='Número de dosis administrada, si aplica (ej. 1, 2, 3).'
    )
    next_dose_date = models.DateField(
        'Fecha Próxima Dosis',
        blank=True,
        null=True,
        help_text='Fecha estimada para la siguiente dosis, si aplica.'
    )
    notes = models.TextField(
        'Notas Adicionales',
        blank=True,
        null=True
    )
    vaccine_file = models.FileField(
        upload_to='vaccination_records/',
        verbose_name='Archivo de Vacunación',
        blank=True,
        null=True
    )

    @property
    def days_to_next_dose(self):
        """
        Calcula los días restantes para la próxima dosis.
        """
        if self.next_dose_date:
            return (self.next_dose_date - self.application_date).days
        return 0

    @property
    def next_dose(self):
        """
        
        """
        return self.next_dose_date

    @classmethod
    def get_all_by_technical(cls, technical_id):
        """
        Obtiene todos los registros de vacunación de un técnico específico.
        """
        return cls.objects.filter(
            technical_id=technical_id, is_active=True
        ).order_by('-application_date')

    def __str__(self):
        return f'{self.technical} - {self.get_vaccine_type_display()} ({self.application_date})'

    class Meta:
        verbose_name = 'Registro de Vacunación'
        verbose_name_plural = 'Registros de Vacunación'
        ordering = ['technical', '-application_date']
