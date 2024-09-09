# Estos son los turnos de trabajo, los empleados tienen turnos de 22 días de trabajo y 8 días de descanso
from .Technical import Technical
from common import BaseModel
from django.db import models

TYPES = [
    ('free', 'Libre'),
    ('work', 'Trabajo')
]


class WorkShifts(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    technical = models.ForeignKey(
        Technical,
        on_delete=models.CASCADE
    )
    type = models.CharField(
        'Tipo',
        max_length=10,
        choices=TYPES
    )
    date_start = models.DateField(
        'Fecha de Inicio'
    )
    date_end = models.DateField(
        'Fecha de Fin'
    )

    def __str__(self):
        return f'{self.technical} - {self.date_start} - {self.date_end}'

    class Meta:
        unique_together = ('technical', 'date_start')
