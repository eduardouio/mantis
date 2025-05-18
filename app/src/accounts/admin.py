from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth.admin import UserAdmin

from accounts.models import (
    CustomUserModel, License, Technical, VaccinationRecord, PassTechnical, PassVehicle
)
from accounts.forms import CustomCreationForm, CustomChangeForm

admin.site.site_header = "MANTIS GESTION DE MANTENIMIENTOS"
admin.site.site_title = "MANTIS GESTION DE MANTENIMIENTOS"
admin.site.index_title = "PEISOL SA"


class CustomUserModelAdmin(UserAdmin):
    add_form = CustomCreationForm
    form = CustomChangeForm

    model = CustomUserModel

    fieldsets = (
        ('Basico', {
            'fields': (
                'email',  'password', 'is_active',
            )
        }
        ),
        ('Información Personal', {
            'fields': (
                'first_name', 'last_name'
            )
        }
        ),
        ('Permisos', {
            'fields': (
                'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }
        ),
    )
    add_fieldsets = (
        ('Básico', {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'is_staff', 'is_active'
            )
        }
        ),
    )

    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_confirmed_mail',
    )

    list_filter = (
        'is_active',
        'is_confirmed_mail',
    )

    search_fields = ('email', 'first_name', 'last_name')

    ordering = ('-date_joined',)


class LicenseAdmin(SimpleHistoryAdmin):
    list_display = (
        'license_key',
        'activated_on',
        'expires_on',
        'is_active',
        'user',
    )

    list_filter = (
        'is_active',
    )

    search_fields = ('license_key', 'user__first_name', 'user__last_name')

    ordering = ('-created_at',)


class TechnicalAdmin(SimpleHistoryAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'dni',
        'nro_phone',
        'work_area',
        'is_iess_affiliated',
        'has_life_insurance_policy',
        'is_active',
    )

    list_filter = (
        'work_area',
        'is_active',
        'is_iess_affiliated',
        'has_life_insurance_policy',
    )

    search_fields = ('first_name', 'last_name', 'email', 'dni')

    ordering = ('-created_at',)


class VaccinationRecordAdmin(SimpleHistoryAdmin):
    list_display = (
        'technical',
        'vaccine_type',
        'application_date',
        'next_dose_date',
        'created_at',
        'batch_number',
        'updated_at',
    )
    list_filter = (
        'vaccine_type',
        'technical',
        'application_date',
    )
    search_fields = (
        'batch_number',
        'technical__first_name',
        'technical__last_name',
        'vaccine_type',
    )
    autocomplete_fields = ['technical']
    ordering = ('-application_date',)


class PassTechnicalAdmin(SimpleHistoryAdmin):
    list_display = (
        'bloque',
        'fecha_caducidad',
    )
    list_filter = (
        'bloque',
        'fecha_caducidad',
    )
    search_fields = (
        'bloque',
    )
    ordering = ('-fecha_caducidad',)


class PassVehicleAdmin(SimpleHistoryAdmin):
    list_display = (
        'vehicle',
        'bloque',
        'fecha_caducidad',
    )
    list_filter = (
        'bloque',
        'fecha_caducidad',
    )
    search_fields = (
        'vehicle__no_plate',
        'bloque',
    )
    ordering = ('-fecha_caducidad',)


admin.site.register(CustomUserModel, CustomUserModelAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Technical, TechnicalAdmin)
admin.site.register(VaccinationRecord, VaccinationRecordAdmin)
admin.site.register(PassTechnical, PassTechnicalAdmin)
admin.site.register(PassVehicle, PassVehicleAdmin)
