from django.db import models
from common import BaseModel
from django.core.exceptions import ObjectDoesNotExist
from datetime import date

TYPE_CHOISES = (
    ('EQUIPO', 'EQUIPO'),
    ('SERVICIO', 'SERVICIO')
)

EQUIPOS_SUBTIPO = (
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

UNIDAD_CAPACIDAD_CHOICES = (
    ('GALONES', 'GALONES'),
    ('LITROS', 'LITROS'),
    ('METROS_CUBICOS', 'METROS CÚBICOS'),
    ('BARRILES', 'BARRILES'),
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
        choices=TYPE_CHOISES,
        default='EQUIPO'
    )

    # Nuevo campo para subtipo de equipo
    subtipo = models.CharField(
        'Subtipo de Equipo',
        max_length=255,
        choices=EQUIPOS_SUBTIPO,
        blank=True,
        null=True
    )

    brand = models.CharField(
        'Marca',
        max_length=255,
        default='SIN MARCA'
    )
    model = models.CharField(
        'Modelo',
        max_length=255,
        blank=True,
        null=True,
        default='N/A'
    )
    code = models.CharField(
        'Código Equipo',
        max_length=50,
        unique=True
    )
    serial_number = models.CharField(
        'Número de Serie',
        max_length=255,
        blank=True,
        null=True,
        unique=True
    )
    date_purchase = models.DateField(
        'Fecha de Compra',
        blank=True,
        null=True,
        default=None
    )
    height = models.PositiveSmallIntegerField(
        'Altura',
        blank=True,
        null=True,
        default=None
    )
    width = models.PositiveSmallIntegerField(
        'Ancho',
        blank=True,
        null=True,
        default=None
    )
    depth = models.PositiveSmallIntegerField(
        'Profundidad',
        blank=True,
        null=True,
        default=None
    )
    weight = models.PositiveSmallIntegerField(
        'Peso',
        blank=True,
        null=True,
        default=None
    )
    status = models.CharField(
        'Estado',
        max_length=255,
        choices=STATUS_CHOICES,
        default='DISPONIBLE'
    )

    # Campos de capacidad separados
    capacidad = models.DecimalField(
        'Capacidad',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Capacidad del equipo (valor numérico)'
    )

    unidad_capacidad = models.CharField(
        'Unidad de Capacidad',
        max_length=20,
        choices=UNIDAD_CAPACIDAD_CHOICES,
        blank=True,
        null=True,
        help_text='Unidad de medida para la capacidad'
    )

    # Mantener el campo anterior para compatibilidad (deprecated)
    capacidad_galones = models.DecimalField(
        'Capacidad en Galones (Deprecated)',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Campo obsoleto - usar capacidad + unidad_capacidad'
    )

    # Campo específico para plantas de tratamiento de agua residual
    capacidad_planta = models.CharField(
        'Capacidad de Planta',
        max_length=10,
        choices=CAPACIDAD_PLANTA_CHOICES,
        blank=True,
        null=True,
        help_text='Solo para plantas de tratamiento de agua residual'
    )

    # Campos específicos para LAVAMANOS
    bombas_pie = models.BooleanField(
        'Bombas de Pie',
        default=False,
        help_text='Solo para lavamanos'
    )
    dispensador_jabon_lavamanos = models.BooleanField(
        'Dispensador de Jabón',
        default=False,
        help_text='Solo para lavamanos'
    )

    # Campos específicos para BATERÍAS SANITARIAS (HOMBRE Y MUJER)
    dispensador_papel = models.BooleanField(
        'Dispensador de Papel',
        default=False,
        help_text='Para baterías sanitarias'
    )
    dispensador_jabon = models.BooleanField(
        'Dispensador de Jabón',
        default=False,
        help_text='Para baterías sanitarias'
    )
    dispensador_servilletas = models.BooleanField(
        'Dispensador de Servilletas',
        default=False,
        help_text='Para baterías sanitarias'
    )
    urinales = models.BooleanField(
        'Urinales',
        default=False,
        help_text='Solo para baterías sanitarias de hombre'
    )
    asientos = models.BooleanField(
        'Asientos',
        default=False,
        help_text='Para baterías sanitarias'
    )
    bomba_bano = models.BooleanField(
        'Bomba Baño',
        default=False,
        help_text='Para baterías sanitarias'
    )
    bomba_lavamanos = models.BooleanField(
        'Bomba Lavamanos',
        default=False,
        help_text='Para baterías sanitarias'
    )
    tapa_inodoro = models.BooleanField(
        'Tapa de Inodoro',
        default=False,
        help_text='Para baterías sanitarias'
    )
    bases_banos = models.BooleanField(
        'Bases Baños',
        default=False,
        help_text='Para baterías sanitarias'
    )
    tubo_ventilacion = models.BooleanField(
        'Tubo de Ventilación',
        default=False,
        help_text='Para baterías sanitarias'
    )

    # Campo para motivo de reparación
    motivo_reparacion = models.TextField(
        'Motivo de Reparación',
        blank=True,
        null=True,
        help_text='Especificar motivo cuando el estado sea "EN REPARACION"'
    )

    # Estos campos se actualizan cada vez que el equipo cambia de proyecto
    # o de ubicación, no se actualiza manualmente
    # se libera cuando un proyecto termina, o libera el equipo
    bg_current_location = models.CharField(
        'Ubicación Actual',
        max_length=255,
        blank=True,
        null=True
    )
    bg_current_project = models.SmallIntegerField(
        'ID Proyecto Actual',
        blank=True,
        null=True
    )
    bg_date_commitment = models.DateField(
        'Fecha de Compromiso',
        blank=True,
        null=True
    )
    bg_date_free = models.DateField(
        'Fecha de Liberación',
        blank=True,
        null=True
    )

    # Campos para equipos especiales (blower, motor, banda, etc.)
    blower_marca = models.CharField(
        'Marca del Blower',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    blower_modelo = models.CharField(
        'Modelo del Blower',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    motor_marca = models.CharField(
        'Marca del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    motor_modelo = models.CharField(
        'Modelo del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    banda_marca = models.CharField(
        'Marca de la Banda',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    banda_modelo = models.CharField(
        'Modelo de la Banda',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    banda_tipo = models.CharField(
        'Tipo de Banda',
        max_length=1,
        choices=(('A', 'A'), ('B', 'B')),
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques. Solo una por equipo.'
    )
    polea_blower_marca = models.CharField(
        'Marca de la Polea del Blower',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    polea_blower_modelo = models.CharField(
        'Modelo de la Polea del Blower',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    polea_motor_marca = models.CharField(
        'Marca de la Polea del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    polea_motor_modelo = models.CharField(
        'Modelo de la Polea del Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    tablero_electrico_marca = models.CharField(
        'Marca del Tablero Eléctrico',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    tablero_electrico_modelo = models.CharField(
        'Modelo del Tablero Eléctrico',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    guarda_motor_marca = models.CharField(
        'Marca de la Guarda Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )
    guarda_motor_modelo = models.CharField(
        'Modelo de la Guarda Motor',
        max_length=255,
        blank=True,
        null=True,
        help_text='Solo para plantas y tanques'
    )

    def clean(self):
        """Validaciones personalizadas del modelo"""
        from django.core.exceptions import ValidationError

        # Validar que si el estado es "EN REPARACION" se especifique el motivo
        if self.status == 'EN REPARACION' and not self.motivo_reparacion:
            raise ValidationError({
                'motivo_reparacion': 'Debe especificar el motivo de reparación cuando el estado es "EN REPARACION"'
            })

        # Validar que los campos específicos solo se usen con los subtipos correctos
        if self.subtipo == 'LAVAMANOS':
            # Solo validar campos específicos de lavamanos
            pass
        elif self.subtipo in ['BATERIA SANITARIA HOMBRE', 'BATERIA SANITARIA MUJER']:
            # Validar que urinales solo se use en baterías de hombre
            if self.subtipo == 'BATERIA SANITARIA MUJER' and self.urinales:
                raise ValidationError({
                    'urinales': 'Los urinales solo aplican para baterías sanitarias de hombre'
                })
        elif self.subtipo == 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL':
            # Validar que se especifique la capacidad de planta
            if not self.capacidad_planta:
                raise ValidationError({
                    'capacidad_planta': 'Debe especificar la capacidad de la planta para este tipo de equipo'
                })

        # Validar que los campos de blower, motor, banda, etc. solo se llenen para los subtipos correctos
        subtipos_especiales = [
            'PLANTA DE TRATAMIENTO DE AGUA',
            'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL',
            'TANQUES DE ALMACENAMIENTO AGUA CRUDA',
            'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL'
        ]
        campos_especiales = [
            'blower_marca', 'blower_modelo', 'motor_marca', 'motor_modelo',
            'banda_marca', 'banda_modelo', 'banda_tipo',
            'polea_blower_marca', 'polea_blower_modelo',
            'polea_motor_marca', 'polea_motor_modelo',
            'tablero_electrico_marca', 'tablero_electrico_modelo',
            'guarda_motor_marca', 'guarda_motor_modelo'
        ]
        if self.subtipo not in subtipos_especiales:
            for campo in campos_especiales:
                if getattr(self, campo):
                    raise ValidationError({
                        campo: f'Este campo solo aplica para plantas y tanques.'
                    })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def capacidad_display(self):
        """Muestra la capacidad con su unidad de forma legible"""
        if self.capacidad and self.unidad_capacidad:
            unidad_display = dict(UNIDAD_CAPACIDAD_CHOICES).get(
                self.unidad_capacidad, self.unidad_capacidad)
            return f"{self.capacidad} {unidad_display}"
        elif self.capacidad_galones:  # Fallback al campo anterior
            return f"{self.capacidad_galones} Galones"
        return "No especificada"

    @property
    def tiene_caracteristicas_especiales(self):
        """Verifica si el equipo tiene características específicas configuradas"""
        caracteristicas = [
            self.bombas_pie, self.dispensador_jabon_lavamanos, self.dispensador_papel,
            self.dispensador_jabon, self.dispensador_servilletas, self.urinales,
            self.asientos, self.bomba_bano, self.bomba_lavamanos, self.tapa_inodoro,
            self.bases_banos, self.tubo_ventilacion
        ]
        return any(caracteristicas)

    @property
    def caracteristicas_activas(self):
        """Retorna una lista de las características activas del equipo"""
        caracteristicas = []

        if self.subtipo == 'LAVAMANOS':
            if self.bombas_pie:
                caracteristicas.append('Bombas de Pie')
            if self.dispensador_jabon_lavamanos:
                caracteristicas.append('Dispensador de Jabón')

        elif self.subtipo in ['BATERIA SANITARIA HOMBRE', 'BATERIA SANITARIA MUJER']:
            if self.dispensador_papel:
                caracteristicas.append('Dispensador de Papel')
            if self.dispensador_jabon:
                caracteristicas.append('Dispensador de Jabón')
            if self.dispensador_servilletas:
                caracteristicas.append('Dispensador de Servilletas')
            if self.urinales:
                caracteristicas.append('Urinales')
            if self.asientos:
                caracteristicas.append('Asientos')
            if self.bomba_bano:
                caracteristicas.append('Bomba Baño')
            if self.bomba_lavamanos:
                caracteristicas.append('Bomba Lavamanos')
            if self.tapa_inodoro:
                caracteristicas.append('Tapa de Inodoro')
            if self.bases_banos:
                caracteristicas.append('Bases Baños')
            if self.tubo_ventilacion:
                caracteristicas.append('Tubo de Ventilación')

        return caracteristicas

    @classmethod
    def get_by_id(cls, id_equipment):
        try:
            return ResourceItem.objects.get(id=id_equipment)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_free_equipment(cls):
        today = date.today()
        return cls.objects.filter(
            status='DISPONIBLE',
            is_active=True,
            type='EQUIPO',
            bg_date_free__lte=today
        )

    def __str__(self):
        capacidad_str = f" - {self.capacidad_display}" if (
            self.capacidad or self.capacidad_galones) else ""
        if self.subtipo == 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL' and self.capacidad_planta:
            capacidad_str = f" - {self.capacidad_planta}"
        return f"{self.name}{capacidad_str}"

    class Meta:
        verbose_name = 'Recurso/Equipo'
        verbose_name_plural = 'Recursos/Equipos'
        ordering = ['name']
