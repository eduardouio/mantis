from django.db import models
from common import BaseModel
from projects.models import Partner
from equipment.models import Equipment

SERVICES_CHOICES = (
    ('ALQUILER', 'ALQUILER DE EQUIPOS'),
    ('MANTENIMIENTO', 'MANTENIMIENTO Y LIMPIEZA DE EQUIPO SANITARIO'),
)


class Project(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    internal_code = models.CharField(
        'Código Interno',
        max_length=100,
        help_text='PSL-PS-000109-24'
    )
    partner = models.ForeignKey(
        'projects.Partner',
        on_delete=models.CASCADE
    )
    required_by = models.CharField(
        'Requerido por',
        max_length=255
    )
    autorized_by = models.CharField(
        'Autorizado por',
        max_length=255
    )
    project_name = models.CharField(
        'Nombre del Proyecto',
        max_length=255
    )
    project_description = models.TextField(
        'Descripción del Proyecto',
        blank=True,
        null=True
    )
    place = models.CharField(
        'Lugar',
        max_length=255
    )
    contact_name = models.CharField(
        'Nombre de Contacto',
        max_length=255
    )
    position_contact = models.CharField(
        'Cargo de Contacto',
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
    is_active = models.BooleanField(
        'Activo',
        default=True
    )
    type_service = models.CharField(
        'Tipo de Servicio',
        max_length=255,
        choices=SERVICES_CHOICES
    )

    def __str__(self):
        return self.project_name


class ProjectEquipments(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE
    )
    cost_rent = models.DecimalField(
        'Costo',
        max_digits=10,
        decimal_places=2
    )
    cost_manteinance = models.DecimalField(
        'Costo de Mantenimiento',
        max_digits=10,
        decimal_places=2
    )
    mantenance_frequency = models.CharField(
        'Frecuencia de Mantenimiento',
        max_length=255
    )
    start_date = models.DateField(
        'Fecha de Inicio Operaciones'
    )
    end_date = models.DateField(
        'Fecha de Fin Operaciones'
    )
    is_active = models.BooleanField(
        'Equipo Activo',
        default=True
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
