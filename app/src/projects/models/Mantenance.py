from django.db import models
from common import BaseModel
from projects.models import Project
from equipment.models import Equipment, Vehicle
from accounts.models import Technical


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


class Mantenance(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE
    )
    tecnical = models.ForeignKey(
        Technical,
        on_delete=models.CASCADE
    )
    vehicle = models.ForeignKey(
        'equipment.Vehicle',
        on_delete=models.CASCADE
    )
    date = models.DateField(
        'Fecha'
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
        max_digits=5,
        decimal_places=2
    )
    destination_site = models.CharField(
        'Destino',
        max_length=255
    )
    authorized_by = models.CharField(
        'Autorizado por',
        max_length=255
    )
    authorizing_position = models.CharField(
        'Cargo Autorizador',
        max_length=255
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

    def __str__(self):
        return self.project


class MantenanceSupplies(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    mantenance = models.ForeignKey(
        Mantenance,
        on_delete=models.CASCADE
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE
    )
    make_vaccum = models.BooleanField(
        'Succión',
        default=False
    )
    make_cleaning = models.BooleanField(
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
    use_soap = models.BooleanField(
        'Jabón',
        default=False
    )
    use_disinfectant = models.BooleanField(
        'Desinfectante',
        default=False
    )
    use_trash_bag = models.BooleanField(
        'Guantes',
        default=False
    )
