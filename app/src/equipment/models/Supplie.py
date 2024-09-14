from django.db import models
from common import BaseModel
from projects.models import Project


class Supplie(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        'Nombre',
        max_length=255
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    description = models.TextField(
        'Descripción',
        blank=True,
        null=True
    )
    min_stock = models.PositiveIntegerField(
        'Stock Mínimo',
        default=0
    )
    max_stock = models.PositiveIntegerField(
        'Stock Máximo',
        default=0
    )

    def __str__(self):
        return self.name


class SupplieStockMovment(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    supplie = models.ForeignKey(
        Supplie,
        on_delete=models.CASCADE
    )
    type_movement = models.CharField(
        'Tipo Movimiento',
        max_length=255,
        choices=(
            ('ENTRADA', 'ENTRADA'),
            ('SALIDA', 'SALIDA')
        )
    )
    quantity = models.PositiveIntegerField(
        'cantidad',
        default=0
    )
    unit_cost = models.DecimalField(
        'Costo Unitario',
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f'{self.supplie} - {self.stock}'
