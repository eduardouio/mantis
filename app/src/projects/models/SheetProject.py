from projects.models.Project import Project
from django.db import models
from app.src.common.BaseModel import BaseModel
from equipment.models.ResourceItem import ResourceItem


class SheetProject(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT
    )
    date = models.DateField(
        'Fecha',
        blank=True,
        null=True
    )
    date_start = models.DateField(
        'Fecha de Inicio',
        blank=True,
        null=True
    )
    date_end = models.DateField(
        'Fecha de Fin',
        blank=True,
        null=True
    )
    status = models.CharField(
        'Estado',
        max_length=50,
        choices=(
            ('IN_PROGRESS', 'En Ejecución'),
            ('FINALIZED', 'Finalizado'),
            ('INVOICED', 'Facturado'),
            ('CANCELLED', 'Cancelado')
        ),
        default='IN_PROGRESS'
    )
    series = models.CharField(
        'Serie',
        max_length=50,
        default='PSL-PS-00000-00'
    )
    service_type = models.CharField(
        'Tipo de Servicio',
        max_length=50,
        default='ALQUILER DE EQUIPOS'
    )
    total_bbls = models.DecimalField(
        'Total de Barriles',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_m3 = models.DecimalField(
        'Total de Metros Cúbicos',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    ref_po_client = models.CharField(
        'Referencia PO Cliente',
        max_length=50,
        blank=True,
        null=True
    )
    ref_contact = models.CharField(
        'Referencia de Contacto',
        max_length=50,
        blank=True,
        null=True
    )
    ref_contact_tel = models.CharField(
        'Referencia de Teléfono de Contacto',
        max_length=50,
        blank=True,
        null=True
    )
    ref_nro_final_disposition = models.CharField(
        'Referencia de Disposición Final',
        max_length=50,
        blank=True,
        null=True
    )
    ref_nro_invoice = models.CharField(
        'Referencia de Factura',
        max_length=50,
        blank=True,
        null=True
    )
    subtotal = models.DecimalField(
        'Monto Total',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    taxes = models.DecimalField(
        'IVA',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        'Total',
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ('project', 'date_start', 'date_end')
        verbose_name = 'Planilla de Proyecto'
        verbose_name_plural = 'Planillas de Proyecto'


class SheetProjectDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    sheet_project = models.ForeignKey(
        SheetProject,
        on_delete=models.PROTECT
    )
    resource_item = models.ForeignKey(
        ProjectResourceItem,
        on_delete=models.PROTECT
    )
    detail = models.TextField(
        'Detalle',
        blank=True,
        null=True
    )
    quantity = models.DecimalField(
        'Cantidad',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    unit_price = models.DecimalField(
        'Precio Unitario',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_line = models.DecimalField(
        'Total Línea',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    unit_measurement = models.CharField(
        'Unidad de Medida',
        max_length=50,
        choices=(
            ('UNITY', 'Unidad'),
            ('DAIS', 'Días')
        ),
        default='DAIS'
    )

    total_price = models.DecimalField(
        'Precio Total',
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ('sheet_project', 'resource_item')
        verbose_name = 'Detalle de Planilla de Proyecto'
        verbose_name_plural = 'Detalles de Planilla de Proyecto'
