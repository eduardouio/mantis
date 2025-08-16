from common.BaseModel import BaseModel
from projects.models.Partner import Partner
from projects.models.PaymentSheet import PaymentSheet
from projects.models.CustodyChain import CustodyChain
from django.db import models


class FinalDispositionCertificate(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT
    )
    payment_sheet = models.ForeignKey(
        PaymentSheet,
        on_delete=models.PROTECT
    )
    nro_document = models.CharField(
        'Número de documento',
        max_length=50,
        blank=True,
        null=True,
        help_text='PSL-CDF-20250731-00305'
    )
    date = models.DateField(
        'Fecha',
        blank=True,
        null=True
    )
    text_document = models.TextField(
        'Documento',
        blank=True,
        null=True
    )
    total_bbl = models.PositiveSmallIntegerField(
        'Total de Barriles',
        default=0
    )
    total_m3 = models.PositiveSmallIntegerField(
        'Total Metros Cubicos',
        default=0
    )


class FinalDispositionCertificateDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    final_disposition_certificate = models.ForeignKey(
        FinalDispositionCertificate,
        on_delete=models.PROTECT
    )
    custody_chain = models.ForeignKey(
        CustodyChain,
        on_delete=models.PROTECT
    )
    quantity = models.DecimalField(
        'Cantidad',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    unit = models.CharField(
        'Unidad',
        max_length=255,
        choices=(
            ''
        )
    )