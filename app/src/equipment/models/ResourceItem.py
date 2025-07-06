from django.db import models
from common import BaseModel
from django.core.exceptions import ObjectDoesNotExist
from datetime import date

TYPE_RECORD = (
    ('EQUIPO', 'EQUIPO'),
    ('SERVICIO', 'SERVICIO')
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

    # Precio base de alquiler del equipo
    base_price = models.DecimalField(
        'Base Rental Price',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Valor base de alquiler del equipo'
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

    def clean(self):
        """Validaciones personalizadas del modelo"""
        from django.core.exceptions import ValidationError

        # Validar que si el estado es "EN REPARACION" se especifique el motivo
        if self.status == 'EN REPARACION' and not self.repair_reason:
            raise ValidationError({
                'repair_reason': 'Debe especificar el motivo de reparación cuando el estado es "EN REPARACION"'
            })

        # Validar que los campos específicos solo se usen con los subtypes correctos
        if self.subtype == 'LAVAMANOS':
            # Solo validar campos específicos de lavamanos
            pass
        elif self.subtype in ['BATERIA SANITARIA HOMBRE', 'BATERIA SANITARIA MUJER']:
            # Validar que urinals solo se use en baterías de hombre
            if self.subtype == 'BATERIA SANITARIA MUJER' and self.urinals:
                raise ValidationError({
                    'urinals': 'Los urinals solo aplican para baterías sanitarias de hombre'
                })
        elif self.subtype == 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL':
            # Validar que se especifique la capacidad de planta
            if not self.plant_capacity:
                raise ValidationError({
                    'plant_capacity': 'Debe especificar la capacidad de la planta para este tipo de equipo'
                })

        # Validar que los campos de blower, motor, banda, etc. solo se llenen para los subtypes correctos
        special_subtypes = [
            'PLANTA DE TRATAMIENTO DE AGUA',
            'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL',
            'TANQUES DE ALMACENAMIENTO AGUA CRUDA',
            'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL'
        ]
        special_fields = [
            'blower_brand', 'blower_model', 'engine_brand', 'engine_model',
            'belt_brand', 'belt_model', 'belt_type',
            'blower_pulley_brand', 'blower_pulley_model',
            'motor_pulley_brand', 'motor_pulley_model',
            'electrical_panel_brand', 'electrical_panel_model',
            'motor_guard_brand', 'motor_guard_model'
        ]
        if self.subtype not in special_subtypes:
            for campo in special_fields:
                if getattr(self, campo):
                    raise ValidationError({
                        campo: f'Este campo solo aplica para plantas y tanques.'
                    })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def capacity_display(self):
        """Muestra la capacidad con su unidad de forma legible"""
        if self.capacity_gallons:
            return f"{self.capacity_gallons} Galones"
        elif self.subtype == 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL' and self.plant_capacity:
            return f"{self.plant_capacity}"
        return "No especificada"

    @property
    def has_characteristics(self):
        """Verifies if the equipment has specific characteristics configured"""
        characteristics = [
            self.foot_pumps, self.sink_soap_dispenser, self.paper_dispenser,
            self.soap_dispenser, self.napkin_dispenser, self.urinals,
            self.seats, self.toilet_pump, self.sink_pump, self.toilet_lid,
            self.bathroom_bases, self.ventilation_pipe
        ]
        return any(characteristics)

    @property
    def get_active_characteristics(self):
        """Returns a list of the equipment's active characteristics"""
        characteristics = []

        if self.subtype == 'LAVAMANOS':
            if self.foot_pumps:
                characteristics.append('Foot Pumps')
            if self.sink_soap_dispenser:
                characteristics.append('Soap Dispenser')
            if self.paper_towels:
                characteristics.append('Paper Towels')

        elif self.subtype in ['BATERIA SANITARIA HOMBRE', 'BATERIA SANITARIA MUJER']:
            if self.paper_dispenser:
                characteristics.append('Paper Dispenser')
            if self.soap_dispenser:
                characteristics.append('Soap Dispenser')
            if self.napkin_dispenser:
                characteristics.append('Napkin Dispenser')
            if self.urinals:
                characteristics.append('Urinals')
            if self.seats:
                characteristics.append('Seats')
            if self.toilet_pump:
                characteristics.append('Toilet Pump')
            if self.sink_pump:
                characteristics.append('Sink Pump')
            if self.toilet_lid:
                characteristics.append('Toilet Lid')
            if self.bathroom_bases:
                characteristics.append('Bathroom Bases')
            if self.ventilation_pipe:
                characteristics.append('Ventilation Pipe')

        return characteristics

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
        if self.subtype == 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL' and self.plant_capacity:
            capacity_str = f" - {self.plant_capacity}"
        elif self.capacity_gallons:
            capacity_str = f" - {self.capacity_gallons} Galones"
        return f"{self.name}{capacity_str}"

    class Meta:
        verbose_name = 'Recurso/Equipo'
        verbose_name_plural = 'Recursos/Equipos'
        ordering = ['name']
        unique_together = (('code', 'serial_number'),)
