from django.db import models
from common import BaseModel
from projects.models import Partner
from equipment.models import ResourceItem
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Technical

SERVICES_CHOICES = (
    ('ALQUILER', 'ALQUILER DE EQUIPOS'),
    ('MANTENIMIENTO', 'MANTENIMIENTO Y LIMPIEZA DE EQUIPO SANITARIO'),
    ('LOGISTICA', 'LOGISTICA DE EQUIPOS'),
)

FRECUENCY_CHOICES = (
    ('DIARIO', 'DIARIO'),
    ('SEMANAL', 'SEMANAL'),
    ('QUINCENAL', 'QUINCENAL'),
    ('MENSUAL', 'MENSUAL'),
    ('BIMENSUAL', 'BIMENSUAL'),
    ('TRIMESTRAL', 'TRIMESTRAL'),
    ('SEMESTRAL', 'SEMESTRAL'),
)

CHOICES_VOLUME_AGUA_RESIDUAL = (
    ('90', '90'),
    ('75', '75'),
    ('60', '60',),
    ('45', '45'),
    ('35', '35'),
    ('15', '15'),
    ('10', '10'),
    ('5', '5')
)


CHOICES_CODE = (
    ('SUCCION', 'SUC'),
    ('LIMPIEZA', 'LP'),
    ('LOGISTICA', 'LOG'),
    ('DESINFECCION', 'DSF'),
    ('MANTENIMIENTO', 'MTO')
)

UNIT = (
    ('GALON', 'GALON'),
    ('METRO CUBICO', 'METRO CUBICO'),
    ('BARRILES', 'BARRILES'),
)

ACCION_CHOICES = (
    ('ENVIO_ORIGEN', 'ENVIO ORIGEN'),
    ('TRANSPORTISTA', 'TRANSPORTISTA'),
    ('DISPOSICION_FINAL', 'DISPOSICION FINAL'),
)


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
        'Lugar',
        max_length=255
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
    # aplica a quipos solamente
    cost_manteinance = models.DecimalField(
        'Costo de Mantenimiento',
        max_digits=10,
        decimal_places=2
    )
    mantenance_frequency = models.CharField(
        'Frecuencia de Mantenimiento',
        choices=FRECUENCY_CHOICES,
        max_length=255
    )
    times_mantenance = models.PositiveSmallIntegerField(
        'Veces de Mantenimiento',
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


class WorkOrder(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT
    )
    work_order = models.CharField(
        'Orden de Trabajo',
        max_length=255
    )
    tecnical = models.ForeignKey(
        Technical,
        on_delete=models.PROTECT
    )
    date = models.DateField(
        'Fecha'
    )

    @classmethod
    def get_by_id(cls, id_work_order):
        try:
            return WorkOrder.objects.get(id=id_work_order)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_by_project(cls, project):
        return WorkOrder.objects.filter(project=project, active=True)

    def __str__(self):
        return self.work_order


class WorkOrderDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.PROTECT
    )
    resource_item = models.ForeignKey(
        ProjectResourceItem,
        on_delete=models.PROTECT
    )
    type_service = models.CharField(
        'Tipo de Servicio',
        max_length=255,
        choices=SERVICES_CHOICES
    )
    cost = models.DecimalField(
        'Costo',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    location = models.CharField(
        'Ubicación',
        max_length=255
    )
    start_hour = models.DateTimeField(
        'Hora de inicio'
    )
    end_hour = models.DateTimeField(
        'Hora de Salida'
    )
    total_hours = models.DecimalField(
        'Horas Totales',
        max_digits=10,
        decimal_places=2,
    )
    origin_site = models.CharField(
        'Origen',
        max_length=255,
        null=True,
        blank=True,
        default=None
    )
    destination_site = models.CharField(
        'Destino',
        max_length=255,
        null=True,
        blank=True,
        default=None
    )
    mat_transported_aguas_negras = models.BooleanField(
        'Aguas Negras',
        default=False
    )
    mat_transported_aguas_grises = models.BooleanField(
        'Aguas Grises',
        default=False
    )
    mat_transported_agua_limpa = models.BooleanField(
        'Agua Limpia',
        default=False
    )
    mat_trasported_lodos_activos = models.BooleanField(
        'Lodos Activos',
        default=False
    )
    mat_trasported_agua_residual_tratada = models.BooleanField(
        'Agua Residual Tratada',
        default=False
    )
    volume_transported = models.CharField(
        'Volumen Transportado',
        max_length=255,
    )
    unit = models.CharField(
        'Unidad',
        max_length=255,
        choices=UNIT
    )

    @classmethod
    def get_by_project_resource(cls, project_resource):
        return WorkOrderMaintenance.objects.filter(
            work_order_detail__resource_item=project_resource
        )


class WorkOrderMaintenance(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    work_order_detail = models.ForeignKey(
        WorkOrderDetail,
        on_delete=models.PROTECT
    )
    work_vaccum = models.BooleanField(
        'Succión',
        default=False
    )
    work_cleaning = models.BooleanField(
        'Limpieza',
        default=False
    )
    use_chemical = models.BooleanField(
        'Desinfección',
        default=False
    )
    use_toilet_paper = models.BooleanField(
        'Papel Higiénico',
        default=False
    )
    use_tz = models.BooleanField(
        'Toalla de papel',
        default=False
    )
    use_soap = models.BooleanField(
        'Jabón',
        default=False
    )
    use_trash_bag = models.BooleanField(
        'Guantes',
        default=False
    )
    use_disinfectant = models.BooleanField(
        'Desinfectante',
        default=False
    )

    def __str__(self):
        return self.work_order
