"""Modelo para la Hoja de Mantenimiento.

Representa el documento físico "HOJA DE MANTENIMIENTO" que registra
las intervenciones preventivas o correctivas realizadas sobre equipos
en un proyecto.

El consecutivo (``sheet_number``) es global y autoincremental,
independiente del proyecto al que pertenece la hoja.
"""

from django.db import models
from django.db.models import Max
from common.BaseModel import BaseModel
from common.validators import validate_pdf_file
from equipment.models import ResourceItem
from projects.models.SheetProject import SheetProject
from accounts.models.Technical import Technical


class SheetMaintenance(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    id_sheet_project = models.ForeignKey(
        SheetProject,
        on_delete=models.PROTECT,
        verbose_name='Hoja de Proyecto'
    )
    sheet_number = models.PositiveBigIntegerField(
        'Número de Hoja',
        unique=True,
        blank=True,
        null=True,
        help_text='Consecutivo automático general (no depende del proyecto).'
    )
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=(
            ('DRAFT', 'BORRADOR'),
            ('CLOSED', 'CERRADO'),
            ('VOID', 'ANULADO'),
        ),
        default='DRAFT'
    )
    responsible_technical = models.ForeignKey(
        Technical,
        on_delete=models.PROTECT,
        verbose_name='Técnico Responsable',
        blank=True,
        null=True,
        default=None
    )
    requested_by = models.CharField(
        'Solicitado Por',
        max_length=255,
        blank=True,
        null=True
    )
    rig = models.CharField(
        'RIG',
        max_length=50,
        blank=True,
        null=True
    )
    resource_item = models.ForeignKey(
        ResourceItem,
        on_delete=models.PROTECT,
        verbose_name='Equipo',
        blank=True,
        null=True
    )
    code = models.CharField(
        'Código',
        max_length=100,
        blank=True,
        null=True
    )
    location = models.CharField(
        'Ubicación',
        max_length=255,
        blank=True,
        null=True
    )
    maintenance_type = models.CharField(
        'Tipo de Mantenimiento',
        max_length=20,
        choices=(
            ('PREVENTIVO', 'PREVENTIVO'),
            ('CORRECTIVO', 'CORRECTIVO'),
        ),
        default='PREVENTIVO'
    )
    start_date = models.DateField(
        'Fecha de Inicio'
    )
    end_date = models.DateField(
        'Fecha de Finalización',
        blank=True,
        null=True
    )
    total_days = models.PositiveIntegerField(
        'Total Días',
        default=0,
        blank=True,
        null=True
    )
    cost_day = models.DecimalField(
		'Costo Día',
		max_digits=10,
		decimal_places=2,
		default=0,
		blank=True,
		null=True
	)
    total_cost = models.DecimalField(
		'Costo Total',
		max_digits=10,
		decimal_places=2,
		default=0,
		blank=True,
		null=True
	)
    maintenance_description = models.TextField(
        'Descripción del Mantenimiento',
        blank=True,
        null=True
    )
    fault_description = models.TextField(
        'Descripción de la Falla',
        blank=True,
        null=True
    )
    possible_causes = models.TextField(
        'Posibles Causas',
        blank=True,
        null=True
    )
    replaced_parts = models.TextField(
        'Repuestos y/o Accesorios Reemplazados',
        blank=True,
        null=True
    )
    observations = models.TextField(
        'Observaciones y Recomendaciones',
        blank=True,
        null=True
    )
    performed_by = models.CharField(
        'Realizado Por',
        max_length=255,
        blank=True,
        null=True
    )
    performed_by_position = models.CharField(
        'Cargo de Quien Realiza',
        max_length=255,
        blank=True,
        null=True
    )
    approved_by = models.CharField(
        'Aprobado Por',
        max_length=255,
        blank=True,
        null=True
    )
    approved_by_position = models.CharField(
        'Cargo de Quien Aprueba',
        max_length=255,
        blank=True,
        null=True
    )
    maintenance_file = models.FileField(
        upload_to='projects/maintenance_sheets/',
        verbose_name='Archivo de Hoja de Mantenimiento',
        validators=[validate_pdf_file],
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        if not self.sheet_number:
            max_number = SheetMaintenance.objects.aggregate(
                max_num=Max('sheet_number')
            )['max_num'] or 0
            self.sheet_number = max_number + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Hoja de Mantenimiento'
        verbose_name_plural = 'Hojas de Mantenimiento'

    def __str__(self):
        return f'Hoja de Mantenimiento N° {self.sheet_number} - Hoja de Proyecto {self.id_sheet_project.id}'
