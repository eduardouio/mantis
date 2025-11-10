from django.db import models
from django.core.exceptions import FieldDoesNotExist
from common.BaseModel import BaseModel
 


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


TNQAAC_FIELDS = [
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


TNQAAR_FIELDS = [
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


class ResourceItem(BaseModel):
    
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
    
    type_equipment = models.CharField(
        'Subtipo de Equipo',
        max_length=255,
        choices=TYPE_EQUIPMENT,
        blank=True,
        null=True,
        help_text='Si es un Servicio este campo en nulo'
    )
    brand = models.CharField(
        'Marca',
        max_length=255,
        blank=True,
        null=True
    )
    model = models.CharField(
        'Modelo',
        max_length=255,
        blank=True,
        null=True,
        default='N/A'
    )
    serial_number = models.CharField(
        'Número de Serie',
        max_length=255,
        blank=True,
        null=True,
    )
    date_purchase = models.DateField(
        'Fecha de Compra',
        blank=True,
        null=True,
        default=None
    )
    height = models.PositiveSmallIntegerField(
        'Altura (cm)',
        blank=True,
        null=True,
        default=None
    )
    width = models.PositiveSmallIntegerField(
        'Ancho (cm)',
        blank=True,
        null=True,
        default=None
    )
    depth = models.PositiveSmallIntegerField(
        'Profundidad (cm)',
        blank=True,
        null=True,
        default=None
    )
    weight = models.PositiveSmallIntegerField(
        'Peso (kg)',
        blank=True,
        null=True,
        default=None
    )
    capacity_gallons = models.DecimalField(
        'Capacidad (galones)',
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

    
    have_foot_pumps = models.BooleanField(
        'Bombas de Pie',
        default=False,
        help_text='Solo para lavamanos'
    )
    have_paper_dispenser = models.BooleanField(
        'Dispensador de Papel',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_soap_dispenser = models.BooleanField(
        'Dispensador de Jabón',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_napkin_dispenser = models.BooleanField(
        'Dispensador de Servilletas',
        default=False,
        help_text='Para baterías sanitarias'
    )
    have_paper_towels = models.BooleanField(
        'Toallas de Papel',
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
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        ordering = ['name']
    
    def __str__(self):
        return f'{self.code} -> {self.name}'
    
    @classmethod
    def _fields_by_type(cls):
        """Mapa tipo -> lista de campos (usa constantes de este módulo)."""
        mapping = {
            'LVMNOS': LVMNOS_FIELDS,
            'BTSNHM': BTSNHM_FIELDS,
            'BTSNMJ': BTSNMJ_FIELDS,
            'EST4UR': EST4UR_FIELDS,
            'CMPRBN': CMPRBN_FIELDS,
            'PTRTAP': PTRTAP_FIELDS,
            'PTRTAR': PTRTAR_FIELDS,
            'TNQAAC': TNQAAC_FIELDS,
            'TNQAAR': TNQAAR_FIELDS,
        }
        return mapping

    @classmethod
    def _metadata_fields(cls):
        
        return [
            'notes', 'created_at', 'updated_at',
            'id_user_created', 'id_user_updated', 'is_active'
        ]

    @classmethod
    def _state_fields_prefix(cls):
        return 'stst_'

    @classmethod
    def common_fields_all_types(cls):
        """Intersección de campos comunes entre todos los tipos definidos.
        Excluye campos de estado y metadatos.
        """
        mapping = cls._fields_by_type()
        lists = [set(fields) for fields in mapping.values() if fields]
        if not lists:
            return []
        intersection = set.intersection(*lists)
        
        intersection = {
            f for f in intersection
            if not f.startswith(cls._state_fields_prefix())
            and f not in cls._metadata_fields()
        }
        
        return sorted(intersection)

    @property
    def all_fields_for_type(self):
        """Campos aplicables al tipo; si no hay lista,
        usa fallback de modelo.
        """
        mapping = self._fields_by_type()
        fields = mapping.get(self.type_equipment)
        if fields:
            return fields
        
        model_field_names = [
            f.name for f in self._meta.get_fields() if hasattr(f, 'attname')
        ]
        return [
            f for f in model_field_names
            if not f.startswith('_')
        ]

    @property
    def state_fields(self):
        prefix = self._state_fields_prefix()
        return [f for f in self.all_fields_for_type if f.startswith(prefix)]

    @property
    def metadata_fields(self):
        return [
            f for f in self._metadata_fields()
        ]

    @property
    def common_fields(self):
        return self.common_fields_all_types()

    @property
    def specific_fields(self):
        """Campos específicos del tipo (excluye comunes,
        estado y metadatos).
        """
        commons = set(self.common_fields)
        state = set(self.state_fields)
        meta = set(self._metadata_fields())
        return [
            f for f in self.all_fields_for_type
            if f not in commons and f not in state and f not in meta
        ]

    def get_field_value(self, field_name: str):
        """Obtiene el valor del campo por nombre, seguro para plantillas.
        Si no existe el campo, retorna None.
        """
        
        aliases = {
            'status': 'stst_status_equipment',
            'availability': 'stst_status_disponibility',
            'commitment_date': 'stst_commitment_date',
            'release_date': 'stst_release_date',
        }
        real_name = aliases.get(field_name, field_name)
        try:
            
            try:
                field = self._meta.get_field(real_name)
                if getattr(field, 'choices', None):
                    display_method = f"get_{real_name}_display"
                    if hasattr(self, display_method):
                        return getattr(self, display_method)()
            except Exception:
                pass
            return getattr(self, real_name)
        except Exception:
            return None

    @classmethod
    def _humanize(cls, name: str) -> str:
        
        return name.replace('_', ' ').replace('stst ', '').strip().title()

    def get_field_label(self, field_name: str) -> str:
        """Obtiene verbose_name del campo si existe;
        si no, humaniza el nombre.
        """
        try:
            field = self._meta.get_field(field_name)
            base_label = str(field.verbose_name)
        except FieldDoesNotExist:
            
            prefix = self._state_fields_prefix()
            if field_name.startswith(prefix):
                base_label = self._humanize(field_name[len(prefix):])
            else:
                base_label = self._humanize(field_name)

        
        label_map = {
            
            'id': 'ID',
            'name': 'Nombre Equipo/Servicio',
            'code': 'Código Equipo/Servicio',
            'type_equipment': 'Subtipo de equipo',
            'brand': 'Marca',
            'model': 'Modelo',
            'serial_number': 'Número de serie',
            'date_purchase': 'Fecha de compra',
            'height': 'Altura (cm)',
            'width': 'Ancho (cm)',
            'depth': 'Profundidad (cm)',
            'weight': 'Peso (kg)',
            'capacity_gallons': 'Capacidad (galones)',
            'plant_capacity': 'Capacidad de Planta',
            'is_service': 'Es servicio',
            
            'stst_status_equipment': 'Estado técnico',
            'stst_status_disponibility': 'Disponibilidad',
            'stst_current_location': 'Ubicación Actual',
            'stst_current_project_id': 'ID del Proyecto Actual',
            'stst_commitment_date': 'Fecha de Ocupación',
            'stst_release_date': 'Fecha de Liberación',
            'stst_repair_reason': 'Motivo de Reparación',
            
            'have_foot_pumps': 'Pedales de pie',
            'have_paper_dispenser': 'Dispensador de papel',
            'have_soap_dispenser': 'Dispensador de jabón',
            'have_napkin_dispenser': 'Dispensador de servilletas',
            'have_paper_towels': 'Toallas de papel',
            'have_urinals': 'Urinarios',
            'have_seat': 'Asiento',
            'have_toilet_pump': 'Bomba de baño',
            'have_sink_pump': 'Bomba de lavamanos',
            'have_toilet_lid': 'Llave de baño',
            'have_bathroom_bases': 'Bases de baño',
            'have_ventilation_pipe': 'Tubo de ventilación',
            
            'relay_engine': 'Marca del Relay del Motor',
            'relay_blower': 'Marca del Relay del Blower',
            'blower_brand': 'Marca del Blower',
            'blower_model': 'Modelo del Blower',
            'engine_fases': 'Fases del Motor',
            'engine_brand': 'Marca del Motor',
            'engine_model': 'Modelo del Motor',
            'belt_brand': 'Marca de la Banda',
            'belt_model': 'Modelo de la Banda',
            'belt_type': 'Tipo de Banda',
            'blower_pulley_brand': 'Marca de la Pulley del Blower',
            'blower_pulley_model': 'Modelo de la Pulley del Blower',
            'motor_pulley_brand': 'Marca de la Pulley del Motor',
            'motor_pulley_model': 'Modelo de la Pulley del Motor',
            'electrical_panel_brand': 'Marca del Panel Eléctrico',
            'electrical_panel_model': 'Modelo del Panel Eléctrico',
            'engine_guard_brand': 'Marca de la Guardia del Motor',
            'engine_guard_model': 'Modelo Guarda Motor',
            'pump_filter': 'Bomba de filtración',
            'pump_pressure': 'Bomba de presión',
            'pump_dosing': 'Bomba dosificadora',
            'sand_carbon_filter': 'Filtro de Arena y Carbón',
            'hidroneumatic_tank': 'Tanque Hidroneumático',
            'uv_filter': 'Filtro UV',
        }

        return label_map.get(field_name, base_label)

    
    def as_field_items(self, field_names):
        """Devuelve [{'name','label','value'}] para nombres de campos.
        """
        items = []
        for name in field_names:
            items.append({
                'name': name,
                'label': self.get_field_label(name),
                'value': self.get_field_value(name),
            })
        return items

    @property
    def present_common_fields(self):
        
        boolean_set = set(self.boolean_fields)
        fields = [f for f in self.common_fields if f not in boolean_set]
        return self.as_field_items(fields)

    @property
    def present_specific_fields(self):
        
        boolean_set = set(self.boolean_fields)
        fields = [f for f in self.specific_fields if f not in boolean_set]
        return self.as_field_items(fields)

    @property
    def present_state_fields(self):
        return self.as_field_items(self.state_fields)

    @property
    def present_metadata_fields(self):
        return self.as_field_items(self.metadata_fields)

    
    @property
    def boolean_fields(self):
        """Devuelve los nombres de campos booleanos aplicables al tipo.
        Excluye campos de estado (stst_*) y metadatos.
        """
        names = []
        for name in self.all_fields_for_type:
            
            if name.startswith(self._state_fields_prefix()):
                continue
            if name in self._metadata_fields():
                continue
            try:
                field = self._meta.get_field(name)
                
                if isinstance(field, models.BooleanField):
                    names.append(name)
            except FieldDoesNotExist:
                
                if name.startswith('have_'):
                    names.append(name)
        return names

    @property
    def present_have_fields(self):
        """Items de checklist (booleanos) para la vista."""
        return self.as_field_items(self.boolean_fields)
