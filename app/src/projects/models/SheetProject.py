from projects.models.Project import Project
from django.db import models
from common.BaseModel import BaseModel
from equipment.models.ResourceItem import ResourceItem
from datetime import datetime


class SheetProject(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT
    )
    issue_date = models.DateField(
        "Fecha de Emisión",
        blank=True,
        null=True
    )
    period_start = models.DateField(
        "Fecha de Inicio",
        blank=True,
        null=True
    )
    period_end = models.DateField(
        "Fecha de Fin",
        blank=True,
        null=True
    )
    status = models.CharField(
        "Estado",
        max_length=50,
        choices=(
            ("IN_PROGRESS", "EN EJECUCIÓN"),
            ("INVOICED", "FACTURADO"),
            ("CANCELLED", "CANCELADO"),
        ),
        default="IN_PROGRESS",
    )
    series_code = models.CharField(
        "Serie",
        max_length=50,
        default="PSL-PS-0000-0000"
    )
    secuence_prefix = models.CharField(
        "Prefijo de Secuencia",
        max_length=10,
        blank=True,
        null=True,
        default="PSL-PS"
    )
    secuence_year = models.PositiveIntegerField(
        "Año de Secuencia",
        blank=True,
        null=True,
        default=datetime.now().year
    )
    secuence_number = models.PositiveIntegerField(
        "Número de Secuencia",
        blank=True,
        null=True,
        default=0
    )
    service_type = models.CharField(
        "Tipo de Servicio",
        max_length=50,
        choices=(
            ("ALQUILER", "ALQUILER"),
            ("MANTENIMIENTO", "MANTENIMIENTO"),
            ("ALQUILER Y MANTENIMIENTO", "ALQUILER Y MANTENIMIENTO"),
        ),
        default="ALQUILER Y MANTENIMIENTO",
    )
    total_gallons = models.PositiveSmallIntegerField(
        "Total de Galones",
        default=0
    )
    total_barrels = models.PositiveSmallIntegerField(
        "Total de Barriles",
        default=0
    )
    total_cubic_meters = models.PositiveSmallIntegerField(
        "Total de Metros Cúbicos",
        default=0
    )
    client_po_reference = models.CharField(
        "Referencia PO Cliente",
        max_length=50,
        blank=True,
        null=True
    )
    contact_reference = models.CharField(
        "Referencia de Contacto",
        max_length=50,
        blank=True,
        null=True
    )
    contact_phone_reference = models.CharField(
        "Referencia de Teléfono de Contacto",
        max_length=50,
        blank=True,
        null=True
    )
    final_disposition_reference = models.CharField(
        "Referencia de Disposición Final",
        max_length=50,
        blank=True,
        null=True
    )
    invoice_reference = models.CharField(
        "Referencia de Factura",
        max_length=50,
        blank=True,
        null=True
    )
    subtotal = models.DecimalField(
        "Monto Total",
        max_digits=10,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        "IVA",
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        "Total",
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ("project", "period_start", "period_end")
        verbose_name = "Planilla de Proyecto"
        verbose_name_plural = "Planillas de Proyecto"

    def __str__(self):
        return f"Planilla {self.id} - Proyecto {self.project.partner.name}"

    @classmethod
    def get_next_series_code(cls):
        """
        Formato: PSL-PS-YYYY-NNNN
        Donde:
            - PSL-PS: Prefijo fijo
            - YYYY: Año actual
            - NNNN: Consecutivo de 4 dígitos empezando en 1000
        """
        current_year = datetime.now().year

        last_sheet = (
            cls.objects.filter(
                secuence_year=current_year,
            )
            .order_by("-secuence_number")
            .first()
        )

        if last_sheet:
            next_number = last_sheet.secuence_number + 1
        else:
            next_number = 1000

        return f"PSL-PS-{current_year}-{next_number:04d}"


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
    )
    quantity = models.DecimalField(
        "Cantidad",
        max_digits=10,
        decimal_places=2,
        default=0
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
        unique_together = ("sheet_project", "resource_item")
        verbose_name = "Detalle de Planilla de Proyecto"
        verbose_name_plural = "Detalles de Planilla de Proyecto"