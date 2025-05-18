from django.db import models
from common import BaseModel
from accounts.models.CustomUserModel import CustomUserModel


ROLE_CHOICES = (
    ('ADMINISTRATIVO', 'ADMINISTRATIVO'),
    ('TECNICO', 'TECNICO'),
)

WORK_AREA_CHOICES = (
    ('PLANT_PROJECTS', 'Proyectos de Plantas de tratamiento de agua'),
    ('SANITARY_TECHNICIAN', 'Técnico de baterías sanitarias'),
    ('ASSISTANT', 'Ayudante'),
    ('MAINTENANCE_LOGISTICS', 'Mantenimientos y Logística'),
    ('SUPERVISOR', 'Supervisor'),
)


class Technical(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    date_joined = models.DateField(
        'Fecha de Ingreso',
        blank=True,
        null=True,
        default=None
    )
    first_name = models.CharField(
        'Nombres',
        max_length=255
    )
    last_name = models.CharField(
        'Apellidos',
        max_length=255
    )
    email = models.EmailField(
        'Correo Electrónico',
        max_length=255,
        blank=True,
        null=True,
        default=None
    )
    
    work_area = models.CharField(
        'Área de Trabajo',
        max_length=255,
        choices=WORK_AREA_CHOICES,
        default='ASSISTANT' 
    )
    dni = models.CharField(
        'Cédula',
        max_length=15
    )
    user = models.OneToOneField(
        CustomUserModel,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None
    )
    nro_phone = models.CharField(
        'Número de Celular',
        max_length=15
    )
    role = models.CharField(
        'cargo', 
        max_length=255,
        choices=ROLE_CHOICES,
    )
    

    
    birth_date = models.DateField(
        'Fecha de Nacimiento',
        blank=True,
        null=True
    )
    license_issue_date = models.DateField(
        'Fecha de Emisión Licencia',
        blank=True,
        null=True
    )
    license_expiry_date = models.DateField(
        'Fecha de Caducidad Licencia',
        blank=True,
        null=True
    )
    defensive_driving_certificate_issue_date = models.DateField(
        'Fecha Emisión Certificado Manejo Defensivo',
        blank=True,
        null=True
    )
    defensive_driving_certificate_expiry_date = models.DateField(
        'Fecha Caducidad Certificado Manejo Defensivo',
        blank=True,
        null=True
    )
    mae_certificate_issue_date = models.DateField(
        'Fecha Emisión Certificado MAE',
        blank=True,
        null=True
    )
    mae_certificate_expiry_date = models.DateField(
        'Fecha Caducidad Certificado MAE',
        blank=True,
        null=True
    )
    medical_certificate_issue_date = models.DateField(
        'Fecha Emisión Certificado Médico',
        blank=True,
        null=True
    )
    medical_certificate_expiry_date = models.DateField(
        'Fecha Caducidad Certificado Médico',
        blank=True,
        null=True
    )
    is_iess_affiliated = models.BooleanField(
        'Afiliado IESS?',
        default=False
    )
    has_life_insurance_policy = models.BooleanField(
        'Póliza de Vida?',
        default=False
    )
    quest_ncst_code = models.CharField(
        'Código Quest NCST',
        max_length=255,
        blank=True,
        null=True
    )
    quest_instructor = models.CharField(
        'Instructor Quest',
        max_length=255,
        blank=True,
        null=True
    )
    quest_start_date = models.DateField(
        'Fecha Inicio Quest',
        blank=True,
        null=True
    )
    quest_end_date = models.DateField(
        'Fecha Fin Quest',
        blank=True,
        null=True
    )
    notes = models.TextField(
        'Notas',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        'Activo?',
        default=False
    )
