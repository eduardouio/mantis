from django.db import models
from .Technical import Technical
from common import BaseModel

CHOICES = (
    ('TRABAJO', 'TRABAJO'),
    ('DESCANSO', 'DESCANSO'),
)


class WorkJournal(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    technical = models.ForeignKey(
        Technical,
        on_delete=models.RESTRICT,
    )
    type = models.CharField(
        'Tipo',
        max_length=10,
        choices=CHOICES,
        default='TRABAJO'
    )
    date_start = models.DateField(
        'fecha de inicio',
    )
    date_end = models.DateField(
        'fecha de fin',
    )
    is_active = models.BooleanField(
        'Activo?',
        default=False
    )
