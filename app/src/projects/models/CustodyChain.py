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
    detail = models.TextField(
        "Detalle",
        blank=True,
        null=True
    )
    item_unity = models.CharField(
        "Unidad del Item",
        max_length=100,
        choices=(
            ("DIAS", "DÍAS"),
            ("UNIDAD", "UNIDAD"),
        ),
        default="DIAS",
    )
    quantity = models.DecimalField(
        "Cantidad",
        max_digits=10,
        decimal_places=2,
        default=1
    )
    unit_price = models.DecimalField(
        "Precio Unitario",
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_line = models.DecimalField(
        "Total Línea",
        max_digits=10,
        decimal_places=2,
        default=0
    )
    unit_measurement = models.CharField(
        "Unidad de Medida",
        max_length=50,
        choices=(
            ("UNITY", "Unidad"),
            ("DAIS", "Días")
        ),
        default="DAIS",
    )
    total_price = models.DecimalField(
        "Precio Total",
        max_digits=10,
        decimal_places=2,
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
