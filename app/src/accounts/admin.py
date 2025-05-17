from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth.admin import UserAdmin

from accounts.models import (
    CustomUserModel, License, Technical, VaccinationRecord
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
        'role',
        'is_active',
        'user',
    )

    list_filter = (
        'role',
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
        'work_area',  # Cambiado de location y se eliminaron days_to_work, days_free
        'role',
        'is_iess_affiliated', # Nuevo campo
        'has_life_insurance_policy', # Nuevo campo
        'is_active',
    )

    list_filter = (
        'role',
        'work_area', # Añadido work_area al filtro
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
        'dose_number',
        'next_dose_date',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'vaccine_type',
        'technical',
        'application_date',
    )
    search_fields = (
        'technical__first_name',
        'technical__last_name',
        'vaccine_type',
    )
    autocomplete_fields = ['technical']
    ordering = ('-application_date',)


admin.site.register(CustomUserModel, CustomUserModelAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Technical, TechnicalAdmin)
admin.site.register(VaccinationRecord, VaccinationRecordAdmin)
