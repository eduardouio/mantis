from django.db import models
from partners.models import Partner
from common import BaseModel


class Technical(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    names = models.CharField(
        'Nombre del Técnico',
        max_length=255
    )
    dni = models.CharField(
        'Cédula',
        max_length=15
    )
    role = models.CharField(
        'Cargo',
        max_length=50
    )
    work_days = models.PositiveIntegerField(
        'dia de trabajo'
    )
    free_days = models.PositiveIntegerField(
        'dias de descanso'
    )
    partner = models.ManyToManyField(
        Partner,
        on_delete=models.CASCADE
    )
    date_start = models.DateField(
        'Fecha de Inicio'
        help_text='Fecha de inicio de jornada laboral para el calculo 22/8'
    )

    def __str__(self):
        return self.nombre
