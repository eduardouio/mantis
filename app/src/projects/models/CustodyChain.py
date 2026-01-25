from django.db import models
from accounts.models.Technical import Technical
from equipment.models.Vehicle import Vehicle
from projects.models.SheetProject import SheetProject
from projects.models.Project import ProjectResourceItem
from common.BaseModel import BaseModel


class CustodyChain(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    status = models.CharField(
        "Estado",
        max_length=50,
        choices=(
            ("DRAFT", "BORRADOR"),
            ("CLOSE", "CERRADO"),
        ),
        default="DRAFT",
    )
    technical = models.ForeignKey(
        Technical,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None
    )
    sheet_project = models.ForeignKey(
        SheetProject,
        on_delete=models.PROTECT
    )
    consecutive = models.CharField(
        'Consecutivo',
        max_length=7,
        blank=True,
        null=True
    )
    activity_date = models.DateField(
        'Fecha'
    )
    location = models.CharField(
        'Ubicación',
        max_length=255,
        blank=True,
        null=True
    )
    issue_date = models.DateField(
        'Fecha de Emisión',
        blank=True,
        null=True
    )
    start_time = models.TimeField(
        'Hora de inicio',
        blank=True,
        null=True
    )
    end_time = models.TimeField(
        'Hora de Salida',
        blank=True,
        null=True
    )
    time_duration = models.DecimalField(
        'Horas Totales',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    contact_name = models.CharField(
        'Nombre de Contacto',
        max_length=255,
        blank=True,
        null=True
    )
    dni_contact = models.CharField(
        'Cédula de Contacto',
        max_length=15,
        blank=True,
        null=True
    )
    contact_position = models.CharField(
        'Cargo de Contacto',
        max_length=255,
        blank=True,
        null=True
    )
    date_contact = models.DateField(
        'Fecha de Contacto',
        blank=True,
        null=True,
        default=None
    )    
    driver_name = models.CharField(
        'Nombre de Transportista',
        max_length=255,
        blank=True,
        null=True
    )
    dni_driver = models.CharField(
        'Cédula de Transportista',
        max_length=15,
        blank=True,
        null=True
    )
    driver_position = models.CharField(
        'Cargo de Transportista',
        max_length=255,
        blank=True,
        null=True
    )
    driver_date = models.DateField(
        'Fecha de Transportista',
        blank=True,
        null=True,
        default=None
    )
    total_gallons = models.PositiveSmallIntegerField(
        'Total de Galones',
        default=0
    )
    total_barrels = models.PositiveSmallIntegerField(
        'Total de Barriles',
        default=0
    )
    total_cubic_meters = models.PositiveSmallIntegerField(
        'Total de Metros Cúbicos',
        default=0
    )
    have_logistic = models.CharField(
        'Se realiza Logística',
        choices=(
            ('SI', 'SI'),
            ('NO', 'NO'),
            ('NA', 'NO APLICA'),
        ),
        default='NA',
        max_length=2
    )


    @classmethod
    def get_next_consecutive(cls):
        """Generar el siguiente consecutivo para una cadena de custodia."""
        last_chain = cls.objects.all().order_by('-id').first()

        if not last_chain:
            return '0000001'

        if last_chain and last_chain.consecutive:
            try:
                last_number = int(last_chain.consecutive)
                next_number = last_number + 1
            except ValueError:
                next_number = 1
        else:
            next_number = 1

        return str(next_number).zfill(7)

    class Meta:
        verbose_name = 'Cadena de Custodia'
        verbose_name_plural = 'Cadenas de Custodia'

    def __str__(self):
        return f'{self.sheet_project.id}-{self.activity_date}'


class ChainCustodyDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    custody_chain = models.ForeignKey(
        CustodyChain,
        on_delete=models.PROTECT
    )
    project_resource = models.ForeignKey(
        ProjectResourceItem,
        on_delete=models.PROTECT
    )

    @classmethod
    def get_by_sheet_project(cls, sheet_project):
        asigns =  cls.objects.filter(
            is_active=True,
            custody_chain__sheet_project=sheet_project,
        )

        if len(asigns) > 0:
            return asigns
        
        return None

    @classmethod
    def get_by_resource_id(cls, resource_id):
        asigns =  cls.objects.filter(
            is_active=True,
            project_resource__id=resource_id,
        )

        if len(asigns) > 0:
            return asigns
        
        return None

    class Meta:
        verbose_name = 'Detalle de Cadena de Custodia'
        verbose_name_plural = 'Detalles de Cadenas de Custodia'

    def __str__(self):
        return '{}-{}'.format(self.custody_chain.id, self.project_resource.id)
