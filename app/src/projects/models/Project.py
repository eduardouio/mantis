from django.db import models
from common.BaseModel import BaseModel
from equipment.models import ResourceItem
from django.core.exceptions import ObjectDoesNotExist


class Project(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    partner = models.ForeignKey(
        'projects.Partner',
        on_delete=models.PROTECT
    )
    TechnicalResponsible = models.CharField(
        'Técnico Responsable',
        max_length=255,
        blank=True,
        null=True
    )
    place = models.CharField(
        'Campamento',
        max_length=50,
        blank=True,
        null=True,
        default=None
    )
    avrebiature = models.CharField(
        'Abreviatura',
        max_length=10,
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

    @classmethod
    def get_project_by_id(cls, id_project):
        try:
            return Project.objects.get(id=id_project)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_equipment(cls, project):
        return ProjectResourceItem.objects.filter(project=project)


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
    cost = models.DecimalField(
        'Costo General',
        max_digits=10,
        decimal_places=2
    )
    cost_manteinance = models.DecimalField(
        'Costo de Mantenimiento',
        max_digits=10,
        decimal_places=2
    )
    mantenance_frequency = models.PositiveIntegerField(
        'Frecuencia de Mantenimiento',
        default=1
    )
    start_date = models.DateField(
        'Fecha de Inicio Operaciones'
    )
    end_date = models.DateField(
        'Fecha de Fin Operaciones'
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

    @classmethod
    def get_by_id(cls, id_project_equipment):
        try:
            return ProjectResourceItem.objects.get(id=id_project_equipment)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_by_project_resource_id(cls, id_project_equipment):
        try:
            return ProjectResourceItem.objects.get(id=id_project_equipment)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_project_equipment(cls, project):
        return ProjectResourceItem.objects.filter(
            project=project, is_active=True
        )

    class Meta:
        unique_together = ('project', 'resource_item')
