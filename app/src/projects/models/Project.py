"""Modelos relacionados con la gestión de proyectos.

Resumen:
    Project:
        Proyecto contratado por un cliente (``partner``).
        Mientras está activo (``is_closed = False``) se pueden asociar recursos
        (equipos / ítems) vía ``ProjectResourceItem``.
        El cierre lógico se controla solo con ``is_closed``; no se eliminan
        registros para preservar el historial,
        para esto se usa el booleando de BaseModel ``is_deleted``.

    ProjectResourceItem:
        Vincula un recurso físico (``ResourceItem``) a un proyecto y registra:
            - Costos de renta y mantenimiento.
            - Frecuencia de mantenimiento en días.
            - Rango de fechas de operación (``start_date`` → ``end_date``).
        Mientras el rango está vigente el recurso puede mostrarse en
        calendarios / mantenimientos. Al retirarse se marca ``is_retired`` y se
        documentan fecha y motivo.

Notas de diseño:
    - IDs: AutoField incremental estándar.
    - No hay borrado físico; se preserva auditoría.
    - Relaciones usan ``PROTECT`` para mantener integridad.
"""

from django.db import models
from common.BaseModel import BaseModel
from equipment.models import ResourceItem


class Project(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    partner = models.ForeignKey(
        'projects.Partner',
        on_delete=models.PROTECT
    )
    place = models.CharField(
        'Campamento',
        max_length=50,
        blank=True,
        null=True,
        default=None
    )
    contact_name = models.CharField(
        'Nombre de Contacto',
        max_length=255
    )
    phone_contact = models.CharField(
        'Teléfono de Contacto',
        max_length=15
    )
    start_date = models.DateField(
        'Fecha de Inicio'
    )
    end_date = models.DateField(
        'Fecha de Fin'
    )
    is_closed = models.BooleanField(
        'Cerrado',
        default=False
    )


class ProjectResourceItem(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT
    )
    resource_item = models.ForeignKey(
        ResourceItem,
        on_delete=models.PROTECT
    )
    cost_rent = models.DecimalField(
        'Costo Renta',
        max_digits=10,
        decimal_places=2
    )
    cost_maintenance = models.DecimalField(
        'Costo de Mantenimiento',
        max_digits=10,
        decimal_places=2
    )
    maintenance_days_frequency = models.PositiveIntegerField(
        'Frecuencia de Mantenimiento (días)',
        default=1
    )
    start_date = models.DateField(
        'Fecha de Inicio Operaciones'
    )
    end_date = models.DateField(
        'Fecha de Fin Operaciones'
    )
    is_retired = models.BooleanField(
        'Retirado',
        default=False
    )
    retired_date = models.DateField(
        'Fecha de Retiro',
        blank=True,
        null=True
    )
    motive_retired = models.TextField(
        'Motivo de Retiro',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Recurso del Proyecto'
        verbose_name_plural = 'Recursos del Proyecto'

    def __str__(self):
        return f'{self.project.partner.name} - {self.resource_item.name}'
