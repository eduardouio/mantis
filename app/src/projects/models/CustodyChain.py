from django.db import models
from app.src.accounts.models.Technical import Technical
from common.BaseModel import BaseModel
from .PaymentSheet import PaymentSheet
from equipment.models.ResourceItem import ResourceItem


class CustodyChain(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    payment_sheet = models.ForeignKey(
        PaymentSheet,
        on_delete=models.PROTECT
    )
    tecnical = models.ForeignKey(
        Technical,
        on_delete=models.PROTECT
    )
    date = models.DateField(
        'Fecha'
    )
    plate_vehicle = models.CharField(
        'Placa del Vehículo',
        max_length=10,
        blank=True,
        null=True
    )
    ref_contact_name = models.CharField(
        'Nombre de Contacto',
        max_length=255,
        blank=True,
        null=True
    )
    ref_contact_position = models.CharField(
        'Cargo de Contacto',
        max_length=255,
        blank=True,
        null=True
    )
    total_gallons = models.DecimalField(
        'Total de Galones',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_bbl = models.DecimalField(
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
    have_sewage = models.BooleanField(
        'Tiene Aguas Residuales',
        default=False
    )
    have_graywater = models.BooleanField(
        'Tiene Aguas Grises',
        default=False
    )
    have_clean_water = models.BooleanField(
        'Tiene Agua Limpia',
        default=False
    )
    have_activated_sludge = models.BooleanField(
        'Tiene Lodos Activados',
        default=False
    )
    have_treated_wastewater = models.BooleanField(
        'Tiene Aguas Residuales Tratadas',
        default=False
    )
    have_clean_grease = models.BooleanField(
        'Tiene Grasas Limpias',
        default=False
    )
    have_logistic = models.BooleanField(
        'Tiene Logística',
        default=False
    )


class CustodyChainDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    custody_chain = models.ForeignKey(
        CustodyChain,
        on_delete=models.PROTECT
    )
    resource_item = models.ForeignKey(
        ResourceItem,
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


class ChainCustodyDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    custody_chain = models.ForeignKey(
        CustodyChain,
        on_delete=models.PROTECT
    )
    resource_item = models.ForeignKey(
        ResourceItem,
        on_delete=models.PROTECT
    )

