from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import ResourceItem, Vehicle, CertificationVehicle


class EquipmentAdmin(SimpleHistoryAdmin):
    pass


class VehicleAdmin(SimpleHistoryAdmin):
    list_display = (
        'no_plate',
        'brand',
        'model',
        'type_vehicle',
        'year',
        'status_vehicle',
        'owner_transport',
        'is_active',
        'created_at',
    )

    list_filter = (
        'type_vehicle',
        'status_vehicle',
        'owner_transport',
        'brand',
        'year',
        'is_active',
        'created_at',
    )

    search_fields = (
        'no_plate',
        'brand',
        'model',
        'year',
        'serial_number',
        'engine_number',
        'chassis_number',
        'owner_transport__name',
        'notes',
    )
    
    ordering = ('-created_at', '-year')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('no_plate', 'brand', 'model', 'type_vehicle', 'year')
        }),
        ('Detalles Técnicos', {
            'fields': ('serial_number', 'engine_number', 'chassis_number', 'color')
        }),
        ('Estado y Propietario', {
            'fields': ('status_vehicle', 'owner_transport', 'is_active')
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'id_user_created', 'id_user_updated'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at', 'id_user_created', 'id_user_updated')
    
    date_hierarchy = 'created_at'


class CertificationVehicleAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'get_vehicle_plate',
        'date_start',
        'date_end',
        'is_active',
        'created_at',
    )

    list_filter = (
        'name',
        'date_start',
        'date_end',
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
        'notes',
    )
    
    ordering = ('-date_start', '-created_at')
    
    fieldsets = (
        ('Información de Certificación', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Vigencia', {
            'fields': ('date_start', 'date_end')
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'id_user_created', 'id_user_updated'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at', 'id_user_created', 'id_user_updated')
    
    date_hierarchy = 'date_start'
    
    def get_vehicle_plate(self, obj):
        return obj.vehicle.no_plate if hasattr(obj, 'vehicle') and obj.vehicle else 'N/A'
    get_vehicle_plate.short_description = 'Placa del Vehículo'


admin.site.register(ResourceItem, EquipmentAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(CertificationVehicle, CertificationVehicleAdmin)
