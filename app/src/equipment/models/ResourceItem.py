from django.db import models
from common.BaseModel import BaseModel
# from django.core.exceptions import ObjectDoesNotExist  # eliminado (no usado)
from datetime import date

TYPE_RECORD = (
    ('EQUIPO', 'EQUIPO'),
    ('SERVICIO', 'SERVICIO')
)

TYPE_FASES = (
    ('MONOFASICO', 'MONOFASICO'),
    ('BIFASICO', 'BIFASICO'),
    ('TRIFASICO', 'TRIFASICO'),
)

TYPE_EQUIPMENT = (
    ('LAVAMANOS', 'LAVAMANOS'),
    ('BATERIA SANITARIA HOMBRE', 'BATERIA SANITARIA HOMBRE'),
    ('BATERIA SANITARIA MUJER', 'BATERIA SANITARIA MUJER'),
    ('PLANTA DE TRATAMIENTO DE AGUA', 'PLANTA DE TRATAMIENTO DE AGUA POTABLE'),
    ('PLANTA DE TRATAMIENTO DE AGUA RESIDUAL',
     'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL'),
    ('TANQUES DE ALMACENAMIENTO AGUA CRUDA',
     'TANQUES DE ALMACENAMIENTO AGUA CRUDA'),
    ('TANQUES DE ALMACENAMIENTO AGUA RESIDUAL',
     'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL'),
    ('CAMPER BAÑO', 'CAMPER BAÑO'),
    ('ESTACION CUADRUPLE URINARIO', 'ESTACION CUADRUPLE URINARIO'),
)

CAPACIDAD_PLANTA_CHOICES = (
    ('10M3', '10M3'),
    ('15M3', '15M3'),
    ('25M3', '25M3'),
)


class ResourceItem(BaseModel):
    TYPE_CHOICES = [
        ('EQUIPO', 'Equipo'),
        ('SERVICIO', 'Servicio'),
    ]

    STATUS_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('RENTADO', 'Rentado'),
        ('EN REPARACION', 'En Reparación'),
        ('FUERA DE SERVICIO', 'Fuera de Servicio'),
    ]

    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        'Nombre Equipo',
        max_length=255
    )
    type = models.CharField(
        'Tipo',
        max_length=255,
        choices=TYPE_RECORD,
        default='EQUIPO'
    )

    # Nuevo campo para subtype de equipo
    subtype = models.CharField(
        'Equipment Subtype',
        max_length=255,
        choices=TYPE_EQUIPMENT,
        blank=True,
        null=True
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
    code = models.CharField(
        'Equipment Code',
        max_length=50,
        unique=True,
        blank=True,
        null=True
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
    status = models.CharField(
        'Status',
        max_length=255,
        choices=STATUS_CHOICES,
        default='DISPONIBLE'
    )

    # Simplificar campos de capacidad - todo en galones
    capacity_gallons = models.DecimalField(
        'Capacity (gallons)',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Capacidad del equipo en galones'
    )

    # Campo específico para plantas de tratamiento de agua residual
    plant_capacity = models.CharField(
        'Plant Capacity',
        max_length=10,
        choices=CAPACIDAD_PLANTA_CHOICES,
        blank=True,
        null=True,
        help_text='Solo para plantas de tratamiento de agua residual'
    )

    # Campos específicos para LAVAMANOS
    foot_pumps = models.BooleanField(
        'Foot Pumps',
        default=False,
        help_text='Solo para lavamanos'
    )
    sink_soap_dispenser = models.BooleanField(
        'Soap Dispenser',
        default=False,
        help_text='Solo para lavamanos'
    )
    paper_towels = models.BooleanField(
        'Paper Towels',
        default=False,
        help_text='Solo para lavamanos'
    )

    # Campos específicos para BATERÍAS SANITARIAS (HOMBRE Y MUJER)
    paper_dispenser = models.BooleanField(
        'Paper Dispenser',
        default=False,
        help_text='Para baterías sanitarias'
    )
    soap_dispenser = models.BooleanField(
        'Soap Dispenser',
        default=False,
        help_text='Para baterías sanitarias'
    )
    napkin_dispenser = models.BooleanField(
        'Dispensador de Servilletas',
        default=False,
        help_text='Para baterías sanitarias'
    )
    urinals = models.BooleanField(
        'Urinarios',
        default=False,
        help_text='Solo para baterías sanitarias de hombre'
    )
    seats = models.BooleanField(
        'Asiento',
        default=False,
        help_text='Para baterías sanitarias'
    )
    toilet_pump = models.BooleanField(
        'Bomba de Baño',
        default=False,
        help_text='Para baterías sanitarias'
    )
    sink_pump = models.BooleanField(
        'Bomba de Lavamanos',
        default=False,
        help_text='Para baterías sanitarias'
    )
    toilet_lid = models.BooleanField(
        'Llave de Baño',
        default=False,
        help_text='Para baterías sanitarias'
    )
    bathroom_bases = models.BooleanField(
        'Bases de Baño',
        default=False,
        help_text='Para baterías sanitarias'
    )
    ventilation_pipe = models.BooleanField(
        'Tubo de Ventilación',
        default=False,
        help_text='Para baterías sanitarias'
    )

    # Campo para motivo de reparación
    repair_reason = models.TextField(
        'Motivo de Reparación',
        blank=True,
        null=True,
        help_text='Especificar motivo cuando el estado sea "EN REPARACION"'
    )

    # Estos campos se actualizan cada vez que el equipo cambia de proyecto
    # o de ubicación, no se actualiza manualmente
    # se libera cuando un proyecto termina, o libera el equipo
    current_location = models.CharField(
        'Ubicación Actual',
        max_length=255,
        blank=True,
        null=True
    )
    current_project_id = models.SmallIntegerField(
        'ID del Proyecto Actual',
        blank=True,
        null=True
    )
    commitment_date = models.DateField(
        'Fecha de Ocupación',
        blank=True,
        null=True
    )
    release_date = models.DateField(
        'Fecha de Liberación',
        blank=True,
        null=True
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
        choices=TYPE_FASES,
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
    motor_guard_brand = models.CharField(
        'Marca de la Guardia del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    motor_guard_model = models.CharField(
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

    def clean(self):
        """Validaciones personalizadas del modelo"""
        from django.core.exceptions import ValidationError

        # Definiciones de campos por subtipo (validaciones dinámicas)
        # Subtipos que comparten accesorios sanitarios
        sanitary_subtypes = [
            'BATERIA SANITARIA HOMBRE',
            'BATERIA SANITARIA MUJER',
            'CAMPER BAÑO',
            'ESTACION CUADRUPLE URINARIO'
        ]
        plant_potable_subtype = 'PLANTA DE TRATAMIENTO DE AGUA'
        plant_residual_subtype = 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL'
        tank_subtypes = [
            'TANQUES DE ALMACENAMIENTO AGUA CRUDA',
            'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL'
        ]

        lavamanos_fields = [
            'foot_pumps', 'sink_soap_dispenser', 'paper_towels'
        ]
        sanitary_fields = [
            'paper_dispenser', 'soap_dispenser', 'napkin_dispenser',
            'urinals', 'seats', 'toilet_pump', 'sink_pump', 'toilet_lid',
            'bathroom_bases', 'ventilation_pipe'
        ]
        plant_common_fields = [
            'blower_brand', 'blower_model', 'engine_brand', 'engine_model',
            'belt_brand', 'belt_model', 'belt_type', 'blower_pulley_brand',
            'blower_pulley_model', 'motor_pulley_brand', 'motor_pulley_model',
            'electrical_panel_brand', 'electrical_panel_model',
            'motor_guard_brand', 'motor_guard_model'
        ]
        plant_potable_only_fields = [
            'pump_filter', 'pump_pressure', 'pump_dosing',
            'sand_carbon_filter', 'hidroneumatic_tank', 'uv_filter'
        ]
        plant_residual_only_fields = ['relay_engine', 'relay_blower']

    # (variables special_* eliminadas por no usarse directamente)

        # Validar que si el estado es "EN REPARACION" se especifique el motivo
        if self.status == 'EN REPARACION' and not self.repair_reason:
            raise ValidationError({
                'repair_reason': 'Indique motivo (estado EN REPARACION)'
            })

    # Validar uso correcto según subtipo
        # Reglas por subtipo
        if self.subtype == 'LAVAMANOS':
            invalid_fields = (sanitary_fields + plant_common_fields +
                              plant_potable_only_fields +
                              plant_residual_only_fields)
            for campo in invalid_fields:
                if getattr(self, campo):
                    raise ValidationError({campo: 'No aplica para Lavamanos'})
        elif self.subtype in sanitary_subtypes:
            if self.subtype == 'BATERIA SANITARIA MUJER' and self.urinals:
                raise ValidationError({'urinals': 'Urinals solo baterías H'})
            invalid_fields = (lavamanos_fields + plant_common_fields +
                              plant_potable_only_fields +
                              plant_residual_only_fields)
            for campo in invalid_fields:
                if getattr(self, campo):
                    raise ValidationError({campo: 'No aplica (sanitario)'})
        elif self.subtype == plant_potable_subtype:
            invalid_fields = (sanitary_fields + lavamanos_fields +
                              plant_residual_only_fields)
            for campo in invalid_fields:
                if getattr(self, campo):
                    raise ValidationError({campo: 'No aplica (potable)'})
        elif self.subtype == plant_residual_subtype:
            if not self.plant_capacity:
                raise ValidationError({'plant_capacity': 'Requerido'})
            invalid_fields = (sanitary_fields + lavamanos_fields +
                              plant_potable_only_fields)
            for campo in invalid_fields:
                if getattr(self, campo):
                    raise ValidationError({campo: 'No aplica (residual)'})
        elif self.subtype in tank_subtypes:
            invalid_fields = (sanitary_fields + lavamanos_fields +
                              plant_potable_only_fields +
                              plant_residual_only_fields)
            for campo in invalid_fields:
                if getattr(self, campo):
                    raise ValidationError({campo: 'No aplica para tanques'})
        else:
            all_fields = (lavamanos_fields + sanitary_fields +
                          plant_common_fields + plant_potable_only_fields +
                          plant_residual_only_fields)
            for campo in all_fields:
                if getattr(self, campo):
                    raise ValidationError({campo: 'No aplica (sin subtipo)'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def capacity_display(self):
        """Muestra la capacidad con su unidad de forma legible"""
        if self.capacity_gallons:
            return f"{self.capacity_gallons} Galones"
        if (self.subtype == 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL' and
                self.plant_capacity):
            return f"{self.plant_capacity}"
        return "No especificada"

    @property
    def has_characteristics(self):
        """Retorna True si existe al menos una característica relevante."""
        chars = [
            self.foot_pumps, self.sink_soap_dispenser, self.paper_towels,
            self.paper_dispenser, self.soap_dispenser, self.napkin_dispenser,
            self.urinals, self.seats, self.toilet_pump, self.sink_pump,
            self.toilet_lid, self.bathroom_bases, self.ventilation_pipe,
            self.blower_brand, self.engine_brand, self.belt_brand,
            self.pump_filter, self.pump_pressure, self.pump_dosing,
            self.sand_carbon_filter, self.hidroneumatic_tank, self.uv_filter,
            self.relay_engine, self.relay_blower
        ]
        return any(chars)

    @property
    def get_active_characteristics(self):
        """Lista de características activas legibles."""
        chars = []
        if self.subtype == 'LAVAMANOS':
            mapping = [
                (self.foot_pumps, 'Foot Pumps'),
                (self.sink_soap_dispenser, 'Soap Dispenser'),
                (self.paper_towels, 'Paper Towels')
            ]
            chars += [label for cond, label in mapping if cond]
        elif self.subtype in [
            'BATERIA SANITARIA HOMBRE', 'BATERIA SANITARIA MUJER',
            'CAMPER BAÑO', 'ESTACION CUADRUPLE URINARIO'
        ]:
            mapping = [
                (self.paper_dispenser, 'Paper Dispenser'),
                (self.soap_dispenser, 'Soap Dispenser'),
                (self.napkin_dispenser, 'Napkin Dispenser'),
                (self.urinals, 'Urinals'),
                (self.seats, 'Seats'),
                (self.toilet_pump, 'Toilet Pump'),
                (self.sink_pump, 'Sink Pump'),
                (self.toilet_lid, 'Toilet Lid'),
                (self.bathroom_bases, 'Bathroom Bases'),
                (self.ventilation_pipe, 'Ventilation Pipe')
            ]
            chars += [label for cond, label in mapping if cond]
        if self.subtype in [
            'PLANTA DE TRATAMIENTO DE AGUA',
            'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL',
            'TANQUES DE ALMACENAMIENTO AGUA CRUDA',
            'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL'
        ]:
            mapping = [
                (self.blower_brand, 'Blower'),
                (self.engine_brand, 'Motor'),
                (self.belt_brand, 'Banda'),
                (self.pump_filter, 'Bomba Filtración'),
                (self.pump_pressure, 'Bomba Presión'),
                (self.pump_dosing, 'Bomba Dosificadora'),
                (self.sand_carbon_filter, 'Filtro Arena/Carbón'),
                (self.hidroneumatic_tank, 'Tanque Hidroneumático'),
                (self.uv_filter, 'Filtro UV'),
                (self.relay_engine, 'Relay Motor'),
                (self.relay_blower, 'Relay Blower')
            ]
            chars += [label for cond, label in mapping if cond]
        return chars

    @classmethod
    def get_free_equipment(cls):
        today = date.today()
        return cls.objects.filter(
            status='DISPONIBLE',
            is_active=True,
            type='EQUIPO',
            release_date__lte=today
        )

    def __str__(self):
        capacity_str = ""
        if (self.subtype == 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL' and
                self.plant_capacity):
            capacity_str = f" - {self.plant_capacity}"
        elif self.capacity_gallons:
            capacity_str = f" - {self.capacity_gallons} Galones"
        return f"{self.name}{capacity_str}"

    class Meta:
        verbose_name = 'Recurso/Equipo'
        verbose_name_plural = 'Recursos/Equipos'
        ordering = ['name']
        unique_together = (('code', 'serial_number'),)
