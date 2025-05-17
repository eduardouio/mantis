from django.db import models
from common import BaseModel
from .Technical import Technical

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


class VaccinationRecord(BaseModel):
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
    application_date = models.DateField(
        'Fecha de Aplicación'
    )
    dose_number = models.PositiveSmallIntegerField(
        'Número de Dosis',
        blank=True,
        null=True,
        help_text='Dejar en blanco si es dosis única o no aplica.'
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

    class Meta:
        verbose_name = 'Registro de Vacunación'
        verbose_name_plural = 'Registros de Vacunación'
        ordering = ['technical', '-application_date']

    def __str__(self):
        return f'{self.technical} - {self.get_vaccine_type_display()} ({self.application_date})'

