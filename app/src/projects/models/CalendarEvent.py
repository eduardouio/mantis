from django.db import models
from common.BaseModel import BaseModel
from projects.models.Project import Project, ProjectResourceItem
from equipment.models.ResourceItem import ResourceItem
from accounts.models import Technical


class CalendarEvent(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        verbose_name='Proyecto'
    )
    title = models.CharField(
        'Título',
        max_length=255
    )
    description = models.TextField(
        'Descripción',
        blank=True,
        null=True
    )
    event_type = models.CharField(
        'Tipo de Evento',
        max_length=50,
        choices=(
            ('MAINTENANCE', 'Mantenimiento'),
            ('INSTALLATION', 'Instalación'),
            ('REMOVAL', 'Retiro'),
            ('INSPECTION', 'Inspección'),
            ('OTHER', 'Otro'),
        ),
        default='MAINTENANCE'
    )
    priority = models.CharField(
        'Prioridad',
        max_length=20,
        choices=(
            ('LOW', 'Baja'),
            ('MEDIUM', 'Media'),
            ('HIGH', 'Alta'),
            ('URGENT', 'Urgente'),
        ),
        default='MEDIUM'
    )
    status = models.CharField(
        'Estado',
        max_length=50,
        choices=(
            ('SCHEDULED', 'Programado'),
            ('IN_PROGRESS', 'En Progreso'),
            ('COMPLETED', 'Completado'),
            ('CANCELLED', 'Cancelado'),
        ),
        default='SCHEDULED'
    )
    start_date = models.DateField(
        'Fecha de Inicio'
    )
    end_date = models.DateField(
        'Fecha de Fin',
        blank=True,
        null=True
    )
    start_time = models.TimeField(
        'Hora de Inicio',
        blank=True,
        null=True
    )
    end_time = models.TimeField(
        'Hora de Fin',
        blank=True,
        null=True
    )
    responsible_technical = models.ForeignKey(
        Technical,
        on_delete=models.PROTECT,
        verbose_name='Técnico Responsable',
        blank=True,
        null=True
    )
    color = models.CharField(
        'Color',
        max_length=20,
        blank=True,
        null=True,
        help_text='Color hexadecimal para mostrar en el calendario. Ej: #FF5733'
    )

    class Meta:
        verbose_name = 'Evento de Calendario'
        verbose_name_plural = 'Eventos de Calendario'
        ordering = ['start_date', 'start_time']

    def __str__(self):
        return f"{self.title} - {self.start_date} ({self.get_status_display()})"


class CalendarEventDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    calendar_event = models.ForeignKey(
        CalendarEvent,
        on_delete=models.PROTECT,
        related_name='details',
        verbose_name='Evento de Calendario'
    )
    resource_item = models.ForeignKey(
        ResourceItem,
        on_delete=models.PROTECT,
        verbose_name='Recurso'
    )
    project_resource_item = models.ForeignKey(
        ProjectResourceItem,
        on_delete=models.PROTECT,
        verbose_name='Recurso de Proyecto',
        blank=True,
        null=True
    )
    description = models.TextField(
        'Descripción de Actividad',
        blank=True,
        null=True
    )
    cost = models.DecimalField(
        'Costo',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    is_completed = models.BooleanField(
        'Completado',
        default=False
    )
    completed_date = models.DateField(
        'Fecha de Completado',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Detalle de Evento de Calendario'
        verbose_name_plural = 'Detalles de Evento de Calendario'

    def __str__(self):
        return f"{self.calendar_event.title} - {self.resource_item.name}"
