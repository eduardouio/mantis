from django.db import models
from .CustomUserModel import CustomUserModel
from common import BaseModel


class WorkJournal(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    technician = models.ForeignKey(
        CustomUserModel,
        on_delete=models.RESTRICT,
    )
    date_start = models.DateField(
        'fecha de inicio',
    )
    date_end = models.DateField(
        'fecha de fin',
    )
