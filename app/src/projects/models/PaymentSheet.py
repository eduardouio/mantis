from django.db import models
from common.BaseModel import BaseModel
from .Partner import Partner


class PaymentSheet(BaseModel):
    id = models.AutoField(primary_key=True)
    id_partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    consecutive = models.CharField(
        'Nro de Planilla',
        default=0

    )
    oc_number = models.CharField(max_length=100)
    date_start = models.DateField(
        'Fecha de Inicio',
        default=models.functions.Now()
    )
    date_end = models.DateField(
        'Fecha de Fin',
        default=models.functions.Now()
    )
    month_execution = models.CharField(
        'Mes de Ejecución',
        max_length=100
    )
    place = models.CharField(
        'Lugar',
        max_length=100
    )
    contact_name = models.CharField(
        'Nombre de Contacto',
        max_length=100
    )
    contact_phone = models.CharField(
        'Teléfono de Contacto',
        max_length=100
    )
    solicite_by = models.CharField(
        'Solicitado por',
        max_length=100
    )


class PaymentSheetDetail(models.Model):
    id = models.AutoField(primary_key=True)
    id_payment_sheet = models.ForeignKey(PaymentSheet, on_delete=models.CASCADE)
    item_description = models.CharField(
        'Descripción del Item',
        max_length=100
    )
    item_detail = models.TextField(
        'Detalle del Item',
    )
    item_quantity = models.PositiveIntegerField(
        'Cantidad del Item',
        default=1
    )
    item_unity = models.CharField(
        'Unidad del Item',
        max_length=100
    )
    item_amount = models.DecimalField(
        'Monto del Item',
        max_digits=10,
        decimal_places=2
    )
    total_line = models.DecimalField(
        'Total de la Línea',
        max_digits=10,
        decimal_places=2
    )
