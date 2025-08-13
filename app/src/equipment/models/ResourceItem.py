from django.db import models
from common.BaseModel import BaseModel
from datetime import date

# opciones Para Campos
FASES_COUNT = (
    ('1', '1 FASE'),
    ('2', '2 FASES'),
    ('3', '3 FASES'),
)

TYPE_EQUIPMENT = (
    ('SERVIC', 'SERVICIO'),
    ('LVMNOS', 'LAVAMANOS'),
    ('BTSNHM', 'BATERIA SANITARIA HOMBRE'),
    ('BTSNMJ', 'BATERIA SANITARIA MUJER'),
    ('EST4UR', 'ESTACION CUADRUPLE URINARIO'),
    ('CMPRBN', 'CAMPER BAÑO'),
    ('PTRTAP', 'PLANTA DE TRATAMIENTO DE AGUA POTABLE'),
    ('PTRTAR', 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL'),
    ('TNQAAC', 'TANQUES DE ALMACENAMIENTO AGUA CRUDA'),
    ('TNQAAR', 'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL'),
)
DISPONIBILITY_STATUS = (
    ('DISPONIBLE', 'DISPONIBLE'),
    ('RENTADO', 'RENTADO'),
    ('FUERA DE SERVICIO', 'FUERA DE SERVICIO'),
)
STATUS_EQUIPMENT = (
    ('FUNCIONANDO', 'FUNCIONANDO'),
    ('DAÑADO', 'DAÑADO'),
    ('INCOMPLETO', 'INCOMPLETO'),
    ('EN REPARACION', 'EN REPARACION'),
)

SERVICES_FIELDS = [
    'id',
    'name',
    'is_service',
    'code',
    'is_active',
    'created_at',
    'updated_at',
    'id_user_created',
    'id_user_updated'
]

# columnas por equipo
LVMNOS_FIELDS = [
    'id',
    'name',
    'is_service',
    'code',
    'type_equipment',
    'brand',
    'model',
    'serial_number',
    'date_purchase',
    'height',
    'width',
    'depth',
    'weight',
    'capacity_gallons',
    'have_foot_pumps',
    'have_soap_dispenser',
    'have_napkin_dispenser',
    'have_paper_towels',
    'stst_repair_reason',
    'stst_status_equipment',
    'stst_status_disponibility',
    'stst_current_location',
    'stst_current_project_id',
    'stst_commitment_date',
    'stst_release_date',
    'is_active',
    'created_at',
    'updated_at',
    'id_user_created',
    'id_user_updated'
]

# check list Batería Sanitaria Hombre
BTSNHM_FIELDS = [
    'id',
    'name',
    'is_service',
    'code',
    'type_equipment',
    'brand',
    'model',
    'serial_number',
    'date_purchase',
    'height',
    'width',
    'depth',
    'weight',
    'capacity_gallons',
    'have_paper_dispenser',
    'have_soap_dispenser',
    'have_napkin_dispenser',
    'have_urinals',
    'have_seat',
    'have_toilet_pump',
    'have_sink_pump',
    'have_toilet_lid',
    'have_bathroom_bases',
    'have_ventilation_pipe',
    'stst_repair_reason',
    'stst_status_equipment',
    'stst_status_disponibility',
    'stst_current_location',
    'stst_current_project_id',
    'stst_commitment_date',
    'stst_release_date',
    'is_active',
    'created_at',
    'updated_at',
    'id_user_created',
    'id_user_updated'
]

# check list Batería Sanitaria Mujer
BTSNMJ_FIELDS = [
    'id',
    'name',
    'is_service',
    'code',
    'type_equipment',
    'brand',
    'model',
    'serial_number',
    'date_purchase',
    'height',
    'width',
    'depth',
    'weight',
    'capacity_gallons',
    'have_paper_dispenser',
    'have_soap_dispenser',
    'have_napkin_dispenser',
    'have_urinals',
    'have_seat',
    'have_toilet_pump',
    'have_sink_pump',
    'have_toilet_lid',
    'have_bathroom_bases',
    'have_ventilation_pipe',
    'stst_repair_reason',
    'stst_status_equipment',
    'stst_status_disponibility',
    'stst_current_location',
    'stst_current_project_id',
    'stst_commitment_date',
    'stst_release_date',
    'is_active',
    'created_at',
    'updated_at',
    'id_user_created',
    'id_user_updated'
]

# check list Estación Cuádruple Urinario
EST4UR_FIELDS = [
    'id',
    'name',
    'is_service',
    'code',
    'type_equipment',
    'brand',
    'model',
    'serial_number',
    'date_purchase',
    'height',
    'width',
    'depth',
    'weight',
    'capacity_gallons',
    'have_paper_dispenser',
    'have_soap_dispenser',
    'have_napkin_dispenser',
    'have_urinals',
    'have_toilet_pump',
    'have_sink_pump',
    'have_toilet_lid',
    'have_foot_pumps',
    'have_paper_towels',
    'stst_repair_reason',
    'stst_status_equipment',
    'stst_status_disponibility',
    'stst_current_location',
    'stst_current_project_id',
    'stst_commitment_date',
    'stst_release_date',
    'is_active',
    'created_at',
    'updated_at',
    'id_user_created',
    'id_user_updated'
]

# check list Camper Baño
CMPRBN_FIELDS = [
    'id',
    'name',
    'is_service',
    'code',
    'type_equipment',
    'brand',
    'model',
    'serial_number',
    'date_purchase',
    'height',
    'width',
    'depth',
    'weight',
    'capacity_gallons',
    'have_paper_dispenser',
    'have_soap_dispenser',
    'have_napkin_dispenser',
    'have_urinals',
    'have_seat',
    'have_toilet_pump',
    'have_sink_pump',
    'have_toilet_lid',
    'have_bathroom_bases',
    'have_ventilation_pipe',
    'have_foot_pumps',
    'have_paper_towels',
    'stst_repair_reason',
    'stst_status_equipment',
    'stst_status_disponibility',
    'stst_current_location',
    'stst_current_project_id',
    'stst_commitment_date',
    'stst_release_date',
    'is_active',
    'created_at',
    'updated_at',
    'id_user_created',
    'id_user_updated'
]
# check list Planta de Tratamiento de Agua Potable
PTRTAP_FIELDS = [
    'id',
    'name',
    'is_service',
    'code',
    'type_equipment',
    'brand',
    'model',
    'serial_number',
    'date_purchase',
    'height',
    'width',
    'depth',
    'weight',
    'capacity_gallons',
    'relay_engine',
    'relay_blower',
    'blower_brand',
    'blower_model',
    'engine_fases',
    'engine_brand',
    'engine_model',
    'belt_brand',
    'belt_model',
    'belt_type',
    'blower_pulley_brand',
    'blower_pulley_model',
    'motor_pulley_brand',
    'motor_pulley_model',
    'electrical_panel_brand',
    'electrical_panel_model',
    'engine_guard_brand',
    'engine_guard_model',
    'pump_filter',
    'pump_pressure',
    'pump_dosing',
    'sand_carbon_filter',
    'hidroneumatic_tank',
    'uv_filter',
    'have_blower_brand',
    'have_belt_brand',
    'have_blower_pulley',
    'have_motor_pulley',
    'have_electrical_panel',
    'have_motor_guard',
    'have_relay_engine',
    'have_relay_blower',
    'have_uv_filter',
    'have_pump_filter',
    'have_pump_dosing',
    'have_pump_pressure',
    'have_engine',
    'have_engine_guard',
    'have_hidroneumatic_tank',
    'have_sand_carbon_filter',
    'stst_repair_reason',
    'stst_status_equipment',
    'stst_status_disponibility',
    'stst_current_location',
    'stst_current_project_id',
    'stst_commitment_date',
    'stst_release_date',
    'is_active',
    'created_at',
    'updated_at',
    'id_user_created',
    'id_user_updated'
]

PTRTAR_FIELDS = [
     'id',
    'name',
    'is_service',
    'code',
    'type_equipment',
    'brand',
    'model',
    'serial_number',
    'date_purchase',
    'height',
    'width',
    'depth',
    'weight',
    'capacity_gallons',
    'relay_engine',
    'relay_blower',
    'blower_brand',
    'blower_model',
    'engine_fases',
    'engine_brand',
    'engine_model',
    'belt_brand',
    'belt_model',
    'belt_type',
    'blower_pulley_brand',
    'blower_pulley_model',
    'motor_pulley_brand',
    'motor_pulley_model',
    'electrical_panel_brand',
    'electrical_panel_model',
    'engine_guard_brand',
    'engine_guard_model',
    'have_blower_brand',
    'have_belt_brand',
    'have_blower_pulley',
    'have_motor_pulley',
    'have_electrical_panel',
    'have_motor_guard',
    'have_relay_engine',
    'have_relay_blower',
    'have_pump_dosing',
    'have_pump_pressure',
    'have_engine',
    'have_engine_guard',
    'have_hidroneumatic_tank',
    'stst_repair_reason', 'stst_status_equipment',
    'stst_status_disponibility', 'stst_current_location',
    'stst_current_project_id', 'stst_commitment_date',
    'stst_release_date',
    'is_active', 'created_at', 'updated_at',
    'id_user_created', 'id_user_updated'
]


class ResourceItem(BaseModel):
    # campos compartidos por Servicio y Equipo
    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        'Nombre Equipo/Servicio',
        max_length=255
    )
    code = models.CharField(
        'Codigo Equipo/Servicio',
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )
    # campos base de equipos
    type_equipment = models.CharField(
        'Equipment Subtype',
        max_length=255,
        choices=TYPE_EQUIPMENT,
        blank=True,
        null=True,
        help_text='Si es un Servicio este campo en nulo'
    )
    brand = models.CharField(
        'Brand',
        max_length=255,
        blank=True,
        null=True
    )
    model = models.CharField(
        'Model',
        max_length=255,
        blank=True,
        null=True,
        default='N/A'
    )
    serial_number = models.CharField(
        'Serial Number',
        max_length=255,
        blank=True,
        null=True,
    )
    date_purchase = models.DateField(
        'Purchase Date',
        blank=True,
        null=True,
        default=None
    )
    height = models.PositiveSmallIntegerField(
        'Height (cm)',
        blank=True,
        null=True,
        default=None
    )
    width = models.PositiveSmallIntegerField(
        'Width (cm)',
        blank=True,
        null=True,
        default=None
    )
    depth = models.PositiveSmallIntegerField(
        'Depth (cm)',
        blank=True,
        null=True,
        default=None
    )
    weight = models.PositiveSmallIntegerField(
        'Weight (kg)',
        blank=True,
        null=True,
        default=None
    )
    capacity_gallons = models.DecimalField(
        'Capacity (gallons)',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Capacidad del equipo en galones'
    )
    plant_capacity = models.CharField(
        'Capacidad de Planta',
        max_length=255,
        blank=True,
        null=True,
        help_text='Capacidad específica para plantas de tratamiento'
    )

    # checklists
    have_foot_pumps = models.BooleanField(
        'Foot Pumps',
        default=False,
        help_text='Solo para lavamanos'
    )
    have_paper_dispenser = models.BooleanField(
        'Paper Dispenser',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_soap_dispenser = models.BooleanField(
        'Soap Dispenser',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_napkin_dispenser = models.BooleanField(
        'Dispensador de Servilletas',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_paper_towels = models.BooleanField(
        'Paper Towels',
        default=False,
        help_text='Para lavamanos y equipos especiales'
    )
    have_urinals = models.BooleanField(
        'Urinarios',
        default=False,
        help_text='Solo para baterías sanitarias de hombre'
    )
    have_seat = models.BooleanField(
        'Asiento',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_toilet_pump = models.BooleanField(
        'Bomba de Baño',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_sink_pump = models.BooleanField(
        'Bomba de Lavamanos',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_toilet_lid = models.BooleanField(
        'Llave de Baño',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_bathroom_bases = models.BooleanField(
        'Bases de Baño',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_ventilation_pipe = models.BooleanField(
        'Tubo de Ventilación',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_blower_brand = models.BooleanField(
        'Tiene Blower',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_belt_brand = models.BooleanField(
        'Tiene Banda',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_blower_pulley = models.BooleanField(
        'Tiene Pulley del Blower',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_motor_pulley = models.BooleanField(
        'Tiene Pulley del Motor',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_electrical_panel = models.BooleanField(
        'Tiene Panel Eléctrico',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_motor_guard = models.BooleanField(
        'Tiene Guarda Motor',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_relay_engine = models.BooleanField(
        'Tiene Relay del Motor',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_relay_blower = models.BooleanField(
        'Tiene Relay del Blower',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_uv_filter = models.BooleanField(
        'Tiene Filtro UV',
        default=False,
        help_text='Para plantas de agua potable'
    )
    have_pump_filter = models.BooleanField(
        'Tiene Bomba de Filtración',
        default=False,
        help_text='Para plantas de agua potable'
    )
    have_pump_dosing = models.BooleanField(
        'Tiene Bomba Dosificadora',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_pump_pressure = models.BooleanField(
        'Tiene Bomba de Presión',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_engine = models.BooleanField(
        'Tiene Motor',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_engine_guard = models.BooleanField(
        'Tiene Guarda del Motor',
        default=False,
        help_text='Para plantas de tratamiento'
    )
    have_hidroneumatic_tank = models.BooleanField(
        'Tiene Tanque Hidroneumático',
        default=False,
        help_text='Para plantas de agua potable'
    )
    have_sand_carbon_filter = models.BooleanField(
        'Tiene Filtro de Arena y Carbón',
        default=False,
        help_text='Para plantas de agua potable'
    )
    # Campos para equipos especiales (blower, motor, banda, etc.)
    relay_engine = models.CharField(
        'Marca del Relay del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para aguas residuales'
    )
    relay_blower = models.CharField(
        'Marca del Relay del Blower',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para aguas residuales'
    )
    blower_brand = models.CharField(
        'Marca del Blower',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    blower_model = models.CharField(
        'Modelo del Blower',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    engine_fases = models.CharField(
        'Fases del Motor',
        max_length=255,
        blank=True,
        null=True,
        choices=FASES_COUNT,
        help_text='solo para plantas'
    )
    engine_brand = models.CharField(
        'Marca del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    engine_model = models.CharField(
        'Modelo del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    belt_brand = models.CharField(
        'Marca de la Banda',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    belt_model = models.CharField(
        'Modelo de la Banda',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    belt_type = models.CharField(
        'Tipo de Banda',
        max_length=1,
        choices=(('A', 'A'), ('B', 'B')),
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques. Solo una por equipo.'
    )
    blower_pulley_brand = models.CharField(
        'Marca de la Pulley del Blower',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    blower_pulley_model = models.CharField(
        'Modelo de la Pulley del Blower',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    motor_pulley_brand = models.CharField(
        'Marca de la Pulley del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    motor_pulley_model = models.CharField(
        'Modelo de la Pulley del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    electrical_panel_brand = models.CharField(
        'Marca del Panel Eléctrico',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    electrical_panel_model = models.CharField(
        'Modelo del Panel Eléctrico',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    engine_guard_brand = models.CharField(
        'Marca de la Guardia del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    engine_guard_model = models.CharField(
        'Modelo Guarda Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )

    # para plantas de agua potable
    pump_filter = models.CharField(
        'Bomba de filtracion',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas de agua potable'
    )
    pump_pressure = models.CharField(
        'Bomba de Presión',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas de agua potable'
    )
    pump_dosing = models.CharField(
        'Bomba Dosificadora',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas de agua potable'
    )
    sand_carbon_filter = models.CharField(
        'Filtro de Arena y Carbón',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas de agua potable'
    )
    hidroneumatic_tank = models.CharField(
        'Tanque Hidroneumático',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas de agua potable'
    )
    uv_filter = models.CharField(
        'Filtro UV',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas de agua potable'
    )
    stst_repair_reason = models.TextField(
        'Motivo de Reparación',
        blank=True,
        null=True,
        help_text='Especificar motivo cuando el estado sea "EN REPARACION"'
    )
    stst_status_equipment = models.CharField(
        'Status',
        max_length=255,
        choices=STATUS_EQUIPMENT,
        default='FUNCIONANDO'
    )
    stst_status_disponibility = models.CharField(
        'Estado de Disponibilidad',
        max_length=255,
        choices=DISPONIBILITY_STATUS,
        default='DISPONIBLE'
    )
    stst_current_location = models.CharField(
        'Ubicación Actual',
        max_length=255,
        blank=True,
        null=True
    )
    stst_current_project_id = models.SmallIntegerField(
        'ID del Proyecto Actual',
        blank=True,
        null=True
    )
    stst_commitment_date = models.DateField(
        'Fecha de Ocupación',
        blank=True,
        null=True
    )
    stst_release_date = models.DateField(
        'Fecha de Liberación',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Resource Item'
        verbose_name_plural = 'Resource Items'
        ordering = ['name']
