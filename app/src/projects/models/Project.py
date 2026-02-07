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
    location = models.CharField(
        'Campamento',
        max_length=50,
        blank=True,
        null=True,
        default=None
    )
    cardinal_point = models.CharField(
        'Punto Cardinal',
        max_length=20,
        blank=True,
        null=True,
        choices=(
            ('NORTE', 'NORTE'),
            ('SUR', 'SUR'),
            ('ESTE', 'ESTE'),
            ('OESTE', 'OESTE'),
            ('NORESTE', 'NORESTE'),
            ('NOROESTE', 'NOROESTE'),
            ('SURESTE', 'SURESTE'),
            ('SUROESTE', 'SUROESTE'),
        ),
        default=None
    )
    contact_name = models.CharField(
        'Nombre de Contacto',
        max_length=255
    )
    contact_phone = models.CharField(
        'Teléfono de Contacto',
        max_length=15
    )
    start_date = models.DateField(
        'Fecha de Inicio'
    )
    end_date = models.DateField(
        'Fecha de Fin',
        blank=True,
        null=True
    )
    is_closed = models.BooleanField(
        'Cerrado',
        default=False
    )

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return f'Proyecto {self.id} - {self.partner.name}'


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
    type_resource = models.CharField(
        'Tipo de Recurso',
        max_length=10,
        choices=(
            ('EQUIPO', 'EQUIPO'),
            ('SERVICIO', 'SERVICIO'),
        ),
        default='SERVICIO'
    )
    detailed_description = models.CharField(
        'Descripción Detallada',
        max_length=120,
        blank=True,
        null=True
    )
    physical_equipment_code = models.PositiveSmallIntegerField(
        'Código de Equipo Físico',
        blank=True,
        null=True,
        default=0
    )
    cost = models.DecimalField(
        'Costo',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    frequency_type = models.CharField(
       'Tipo de Frecuencia',
        max_length=20,
        choices=(
            ('DAY', 'Por intervalo de días'),
            ('WEEK', 'Días de la semana'),
            ('MONTH', 'Días del mes'),
        ),
        default='DAY'
    )
    interval_days = models.PositiveIntegerField(
        'Frecuencia (días)',
        default=2,
        help_text='Usado cuando frequency_type es INTERVALO'
    )
    weekdays = models.JSONField(
        'Días de la Semana',
        blank=True,
        null=True,
        default=None,
        help_text='Lista de días: 0=Lunes, 1=Martes, ..., 6=Domingo. Ej: [0, 2, 4]'
    )
    monthdays = models.JSONField(
        'Días del Mes',
        blank=True,
        null=True,
        default=None,
        help_text='Lista de días del mes. Ej: [1, 15, 28]'
    )
    operation_start_date = models.DateField(
        'Fecha de Inicio Operaciones'
    )
    operation_end_date = models.DateField(
        'Fecha de Fin Operaciones',
        blank=True,
        null=True
    )
    is_retired = models.BooleanField(
        'Retirado',
        default=False
    )
    retirement_date = models.DateField(
        'Fecha de Retiro',
        blank=True,
        null=True
    )
    retirement_reason = models.TextField(
        'Motivo de Retiro',
        blank=True,
        null=True
    )

    @classmethod
    def delete_forever(cls, id_project_resource):
        """Elimina físicamente un recurso de proyecto por su ID."""
        my_project_resource = cls.objects.filter(id=id_project_resource)
        if my_project_resource.exists():
            my_project_resource.delete()
        
        return True

    @classmethod
    def get_by_project(cls, project_id):
        """Obtiene todos los recursos asociados a un proyecto específico."""
        return cls.objects.filter(
            project__id=project_id,
            is_deleted=False
        )

    class Meta:
        verbose_name = 'Recurso del Proyecto'
        verbose_name_plural = 'Recursos del Proyecto'

    def __str__(self):
        return f'{self.project.partner.name} - {self.resource_item.name}'
