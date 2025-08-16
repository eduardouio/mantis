from django.db import models
from app.src.accounts.models.Technical import Technical
from common.BaseModel import BaseModel
from .PaymentSheet import PaymentSheet
from equipment.models.ResourceItem import ResourceItem


class CustodyChain(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    technical = models.ForeignKey(
        Technical,
        on_delete=models.PROTECT,
    )
    payment_sheet = models.ForeignKey(
        PaymentSheet,
        on_delete=models.PROTECT
    )
    date = models.DateField(
        'Fecha'
    )
    ref_contact_name = models.CharField(
        'Nombre de Contacto',
        max_length=255,
        blank=True,
        null=True
    )
    ref_contact_position = models.CharField(
        'Cargo de Contacto',
        max_length=255,
        blank=True,
        null=True
    )
    total_gallons = models.PositiveSmallIntegerField(
        'Total de Galones',
        default=0
    )
    total_bbl = models.PositiveSmallIntegerField(
        'Total de Barriles',
        default=0
    )
    total_m3 = models.PositiveSmallIntegerField(
        'Total de Metros Cúbicos',
        default=0
    )


class CustodyChainDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    custody_chain = models.ForeignKey(
        CustodyChain,
        on_delete=models.PROTECT
    )
    resource_item = models.ForeignKey(
        ResourceItem,
        on_delete=models.PROTECT
    )
    location = models.CharField(
        'Ubicación',
        max_length=255,
        blank=True,
        null=True
    )
    start_hour = models.TimeField(
        'Hora de inicio'
    )
    end_hour = models.TimeField(
        'Hora de Salida'
    )
    total_hours = models.DecimalField(
        'Horas Totales',
        max_digits=10,
        decimal_places=2,
    )


class ChainCustodyDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    custody_chain = models.ForeignKey(
        CustodyChain,
        on_delete=models.PROTECT
    )
    resource_item = models.ForeignKey(
        ResourceItem,
        on_delete=models.PROTECT
    )
