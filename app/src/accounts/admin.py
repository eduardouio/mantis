from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth.admin import UserAdmin

from accounts.models import (
    CustomUserModel,
    License,
    Technical,
    VaccinationRecord,
    PassTechnical
)
from accounts.forms import (
    CustomCreationForm,
    CustomChangeForm
)

admin.site.site_header = "MANTIS GESTION DE MANTENIMIENTOS"
admin.site.site_title = "MANTIS GESTION DE MANTENIMIENTOS"
admin.site.index_title = "PEISOL SA"


class CustomUserModelAdmin(UserAdmin):
    add_form = CustomCreationForm
    form = CustomChangeForm

    model = CustomUserModel

    fieldsets = (
        ('Básico', {
            'fields': (
                'email', 'password', 'is_active', 'role'
            )
        }),
        ('Información Personal', {
            'fields': (
                'first_name', 'last_name', 'picture', 'notes'
            )
        }),
        ('Estado de Cuenta', {
            'fields': (
                'is_confirmed_mail', 'date_joined', 'last_login'
            )
        }),
        ('Permisos', {
            'fields': (
                'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
    )
    add_fieldsets = (
        ('Básico', {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'is_staff', 'is_active', 'role'
            )
        }),
    )

    list_display = (
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'is_confirmed_mail',
        'is_staff',
        'date_joined',
    )

    list_filter = (
        'is_active',
        'is_confirmed_mail',
        'is_staff',
        'role',
        'date_joined',
    )

    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)


class LicenseAdmin(SimpleHistoryAdmin):
    fieldsets = (
        ('Información de Licencia', {
            'fields': (
                'license_key', 'role', 'enterprise', 'user'
            )
        }),
        ('Fechas y Estado', {
            'fields': (
                'activated_on', 'expires_on', 'is_active'
            )
        }),
        ('Configuración', {
            'fields': (
                'licence_file', 'url_server'
            )
        }),
        ('Archivos', {
            'fields': ('license_file',)
        }),
        ('BaseModel Fields', {
            'fields': (
                'notes', 'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
            )
        }),
    )

    list_display = (
        'license_key',
        'user',
        'role',
        'enterprise',
        'activated_on',
        'expires_on',
        'is_active',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'is_active',
        'role',
        'enterprise',
        'activated_on',
        'expires_on',
    )

    search_fields = ('license_key', 'user__first_name',
                     'user__last_name', 'enterprise')
    readonly_fields = ('created_at', 'updated_at',
                       'id_user_created', 'id_user_updated')
    ordering = ('-created_at',)


class TechnicalAdmin(SimpleHistoryAdmin):
    fieldsets = (
        ('Información Personal', {
            'fields': (
                'first_name', 'last_name', 'email', 'dni', 'sex', 'birth_date', 'medical_record_number'
            )
        }),
        ('Contacto y Trabajo', {
            'fields': (
                'nro_phone', 'work_area', 'date_joined', 'file_number'
            )
        }),
        ('Licencias y Certificados', {
            'fields': (
                'license_issue_date', 'license_expiry_date',
                'defensive_driving_certificate_issue_date', 'defensive_driving_certificate_expiry_date',
                'mae_certificate_issue_date', 'mae_certificate_expiry_date',
                'medical_certificate_issue_date', 'medical_certificate_expiry_date'
            )
        }),
        ('Archivos', {
            'fields': (
                'dni_file', 'license_file', 'vaccine_certificate_file'
            )
        }),
        ('Seguros y Afiliaciones', {
            'fields': (
                'is_iess_affiliated', 'has_life_insurance_policy'
            )
        }),
        ('Quest Information', {
            'fields': (
                'quest_ncst_code', 'quest_instructor', 'quest_start_date', 'quest_end_date'
            )
        }),
        ('BaseModel Fields', {
            'fields': (
                'notes', 'is_active', 'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
            )
        }),
    )

    list_display = (
        'first_name',
        'last_name',
        'email',
        'dni',
        'nro_phone',
        'work_area',
        'date_joined',
        'is_iess_affiliated',
        'has_life_insurance_policy',
        'is_active',
        'created_at', 'updated_at',
    )

    list_filter = (
        'work_area',
        'is_active',
        'is_iess_affiliated',
        'has_life_insurance_policy',
        'date_joined',
        'created_at',
    )

    search_fields = (
        'first_name', 'last_name', 'email', 'dni', 'quest_ncst_code', 'file_number', 'medical_record_number'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
    )
    ordering = ('-created_at',)


class VaccinationRecordAdmin(SimpleHistoryAdmin):
    fieldsets = (
        ('Información de Vacunación', {
            'fields': (
                'technical', 'vaccine_type', 'batch_number'
            )
        }),
        ('Fechas', {
            'fields': (
                'application_date', 'next_dose_date'
            )
        }),
        ('Archivos', {
            'fields': ('vaccine_file',)
        }),
        ('BaseModel Fields', {
            'fields': (
                'notes', 'is_active', 'created_at', 'updated_at',
                'id_user_created', 'id_user_updated'
            )
        }),
    )

    list_display = (
        'technical',
        'vaccine_type',
        'application_date',
        'next_dose_date',
        'batch_number',
        'is_active',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'vaccine_type',
        'application_date',
        'is_active',
        'created_at',
    )

    search_fields = (
        'batch_number',
        'technical__first_name',
        'technical__last_name',
        'vaccine_type',
    )

    autocomplete_fields = ['technical']
    readonly_fields = (
        'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
    )
    ordering = ('-application_date',)


class PassTechnicalAdmin(SimpleHistoryAdmin):
    fieldsets = (
        ('Información del Pase', {
            'fields': (
                'technical', 'bloque', 'fecha_caducidad'
            )
        }),
        ('Archivos', {
            'fields': ('pass_file',)
        }),
        ('Estado', {
            'fields': (
                'is_active',
            )
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created',
                'id_user_updated'
            ),
            'classes': ('collapse',)
        }),
    )

    list_display = (
        'technical',
        'bloque',
        'fecha_caducidad',
        'is_active',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'bloque',
        'fecha_caducidad',
        'is_active',
        'created_at',
    )

    search_fields = (
        'technical__first_name',
        'technical__last_name',
        'bloque',
        'notes',
    )

    autocomplete_fields = ['technical']
    ordering = ('-fecha_caducidad', '-created_at')
    readonly_fields = (
        'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
    )


admin.site.register(CustomUserModel, CustomUserModelAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Technical, TechnicalAdmin)
admin.site.register(VaccinationRecord, VaccinationRecordAdmin)
admin.site.register(PassTechnical, PassTechnicalAdmin)
