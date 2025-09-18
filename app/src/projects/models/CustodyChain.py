"""Modelos para la gestión de cadenas de custodia de proyectos.

CustodyChain:
    Representa el documento físico que el técnico lleva a campo. Registra
    datos operativos (recursos usados, tiempos, volúmenes) durante una
    jornada o intervención. Sólo se persiste la información necesaria para
    alimentar la planilla (``SheetProject``) y cálculos asociados.

Objetivo:
    Servir como punto de control (cut-off) y respaldo mínimo auditable de
    lo ocurrido en sitio, sin incorporar ruido operativo irrelevante.

Campos clave:
    - technical: técnico responsable de la operación.
    - sheet_project: vincula la jornada al período facturable.
    - start_hour / end_hour y total_hours: resumen temporal (no se calcula
      automáticamente aquí; puede validarse en signals futuros).
    - volúmenes (total_gallons, total_bbl, total_m3): métricas de consumo /
      producción asociadas.

ChainCustodyDetail:
    Relaciona ítems de recurso concretos usados en la cadena. Permite
    granularidad para auditoría y posteriores reglas de valoración.

Notas de diseño:
    - Relaciones con ``PROTECT`` para evitar pérdida accidental de trazas.
    - Posible mejora: derivar ``total_hours`` si se desea consistencia.
    - Volúmenes pueden consolidarse luego a la planilla.
"""


from django.db import models
from accounts.models.Technical import Technical
from projects.models.SheetProject import SheetProject
from common.BaseModel import BaseModel
from equipment.models.ResourceItem import ResourceItem


class CustodyChain(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    technical = models.ForeignKey(
        Technical,
        on_delete=models.PROTECT,
    )
    sheet_project = models.ForeignKey(
        SheetProject,
        on_delete=models.PROTECT
    )
    consecutive = models.CharField(
        'Consecutivo',
        max_length=6,
        blank=True,
        null=True
    )
    activity_date = models.DateField(
        'Fecha'
    )
    location = models.CharField(
        'Ubicación',
        max_length=255,
        blank=True,
        null=True
    )
    start_time = models.TimeField(
        'Hora de inicio',
        blank=True,
        null=True
    )
    end_time = models.TimeField(
        'Hora de Salida',
        blank=True,
        null=True
    )
    time_duration = models.DecimalField(
        'Horas Totales',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    contact_name = models.CharField(
        'Nombre de Contacto',
        max_length=255,
        blank=True,
        null=True
    )
    contact_position = models.CharField(
        'Cargo de Contacto',
        max_length=255,
        blank=True,
        null=True
    )
    total_gallons = models.PositiveSmallIntegerField(
        'Total de Galones',
        default=0
    )
    total_barrels = models.PositiveSmallIntegerField(
        'Total de Barriles',
        default=0
    )
    total_cubic_meters = models.PositiveSmallIntegerField(
        'Total de Metros Cúbicos',
        default=0
    )

    class Meta:
        verbose_name = 'Cadena de Custodia'
        verbose_name_plural = 'Cadenas de Custodia'

    def __str__(self):
        return f'{self.sheet_project.id}-{self.activity_date}'


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

    class Meta:
        verbose_name = 'Detalle de Cadena de Custodia'
        verbose_name_plural = 'Detalles de Cadenas de Custodia'

    def __str__(self):
        return '{}-{}'.format(self.custody_chain.id, self.resource_item.id)
