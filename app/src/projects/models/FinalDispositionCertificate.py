"""Certificado de Disposición Final (CDF) y su detalle.

FinalDispositionCertificate:
    Documento que cierra el ciclo de una planilla (``SheetProject``).
    Se emite al concluir un período y consolida volúmenes retirados / tratados
    (barriles, galones, m³). No maneja estados: una vez creado queda como
    registro histórico.

Flujo resumido:
    1. Se cierra el período (planilla) del proyecto.
    2. Se generan los totales a partir de cadenas de custodia asociadas.
    3. Se emite el certificado (número, fecha, texto descriptivo y totales).

FinalDispositionCertificateDetail:
    Liga cada cadena de custodia incluida y detalla cantidades normalizadas
    por unidad (bbl, gal, m³) y el concepto (``detail``).

Notas de diseño:
        - ``nro_document`` admite un formato codificado
            (ej: PSL-CDF-YYYYMMDD-#####).
    - Totales agregados podrían validarse contra la suma de los detalles.
    - Relaciones usan ``PROTECT`` para evitar pérdida de trazabilidad.
"""


from common.BaseModel import BaseModel
from projects.models.SheetProject import SheetProject
from projects.models.CustodyChain import CustodyChain
from django.db import models


class FinalDispositionCertificate(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    payment_sheet = models.ForeignKey(
        SheetProject,
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
    total_gallons = models.PositiveSmallIntegerField(
        'Total de Galones',
        default=0
    )
    total_m3 = models.PositiveSmallIntegerField(
        'Total Metros Cubicos',
        default=0
    )

    class Meta:
        verbose_name = 'Certificado de Disposición Final'
        verbose_name_plural = 'Certificados de Disposición Final'

    def __str__(self):
        return self.nro_document


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
    detail = models.CharField(
        'detalle',
        max_length=255,
        default='AGUAS NEGRAS Y GRISES'
    )
    quantity_bbl = models.PositiveSmallIntegerField(
        'Barriles',
        default=0
    )
    quantity_gallons = models.PositiveSmallIntegerField(
        'Galones',
        default=0
    )
    quantity_m3 = models.PositiveSmallIntegerField(
        'Metros Cúbicos',
        default=0
    )
