"""Modelos para planillas de proyectos (SheetProject y detalles).

SheetProject:
    Representa la planilla / período de trabajo facturable de un proyecto.
    Registra un rango (``date_start`` → ``date_end``) y acumula consumo,
    referencias comerciales y totales monetarios. Sirve como punto de control
    ("cut-off") para agrupación de trabajos y generación de factura.

Estados (``status``):
    IN_PROGRESS:
        Período abierto; se pueden seguir agregando detalles.
    INVOICED:
        Planilla facturada; se considera cerrada. Para nuevos trabajos se crea
        una nueva planilla.
    CANCELLED:
        Planilla cancelada; no se agregan más trabajos. Puede migrar a
        INVOICED sólo si se decide facturar lo acumulado.

Notas:
    - Asociada a múltiples cadenas de custodia / recursos vía detalles.
    - No altera el estado del ``Project`` (independiente de ``is_closed``).
    - Campos de totales (bbls, m3, subtotal, impuestos, total) pueden ser
      recalculados por signals o tareas (no implementado aquí).

SheetProjectDetail:
    Ítems detallados de la planilla: recurso, cantidad, precios y medidas.

Pendiente (revisión futura):
        - Verificar consistencia de los choices 'DAIS'/'DIAS' en
            ``unit_measurement``.
"""


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
            ('IN_PROGRESS', 'EN EJECUCIÓN'),
            ('INVOICED', 'FACTURADO'),
            ('CANCELLED', 'CANCELADO')
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
        ResourceItem,
        on_delete=models.PROTECT
    )
    detail = models.TextField(
        'Detalle',
        blank=True,
        null=True
    )
    item_unity = models.CharField(
        'Unidad del Item',
        max_length=100,
        choices=(
            ('DIAS', 'DÍAS'),
            ('UNIDAD', 'UNIDAD'),
        )
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
