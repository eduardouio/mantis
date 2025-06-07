from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from equipment.models import ResourceItem, Vehicle, CertificationVehicle, PassVehicle


class ResourceItemAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'code', 
        'type',
        'brand',
        'model',
        'status',
        'bg_current_location',
        'is_active',
        'created_at',
    )

    list_filter = (
        'type',
        'status',
        'brand',
        'is_active',
        'created_at',
        'date_purchase',
    )

    search_fields = (
        'name',
        'code',
        'brand',
        'model',
        'bg_current_location',
        'notes',
    )
    
    ordering = ('-created_at', 'name')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'type', 'brand', 'model')
        }),
        ('Características Físicas', {
            'fields': ('height', 'width', 'depth', 'weight'),
            'classes': ('collapse',)
        }),
        ('Estado y Ubicación', {
            'fields': ('status', 'bg_current_location', 'bg_current_project', 'is_active')
        }),
        ('Fechas Importantes', {
            'fields': ('date_purchase', 'bg_date_commitment', 'bg_date_free')
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
        'nro_poliza',
        'insurance_company',
        'notes',
    )
    
    ordering = ('-created_at', '-year')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('no_plate', 'brand', 'model', 'type_vehicle', 'year', 'color')
        }),
        ('Detalles Técnicos', {
            'fields': ('serial_number', 'engine_number', 'chassis_number', 'chasis', 'motor_no')
        }),
        ('Estado y Propietario', {
            'fields': ('status_vehicle', 'owner_transport', 'is_active')
        }),
        ('Fechas y Certificaciones', {
            'fields': ('date_matricula', 'due_date_matricula', 'due_date_cert_oper', 'date_mtop', 'date_technical_review')
        }),
        ('Información de Seguros', {
            'fields': ('nro_poliza', 'insurance_company', 'insurance_issue_date', 'insurance_expiration_date'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('duedate_satellite', 'notes'),
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
        'vehicle__no_plate',
        'vehicle__brand',
        'notes',
    )
    
    ordering = ('-date_start', '-created_at')
    
    fieldsets = (
        ('Información de Certificación', {
            'fields': ('vehicle', 'name', 'description', 'is_active')
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
        return obj.vehicle.no_plate if obj.vehicle else 'N/A'
    get_vehicle_plate.short_description = 'Placa del Vehículo'


class PassVehicleAdmin(SimpleHistoryAdmin):
    list_display = (
        'get_vehicle_plate',
        'bloque',
        'fecha_caducidad',
        'is_active',
        'created_at',
    )

    list_filter = (
        'bloque',
        'fecha_caducidad',
        'is_active',
        'created_at',
    )

    search_fields = (
        'vehicle__no_plate',
        'vehicle__brand',
        'bloque',
        'notes',
    )
    
    ordering = ('-fecha_caducidad', '-created_at')
    
    fieldsets = (
        ('Información del Pase', {
            'fields': ('vehicle', 'bloque', 'fecha_caducidad', 'is_active')
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
    
    date_hierarchy = 'fecha_caducidad'
    
    def get_vehicle_plate(self, obj):
        return obj.vehicle.no_plate if obj.vehicle else 'N/A'
    get_vehicle_plate.short_description = 'Placa del Vehículo'


admin.site.register(ResourceItem, ResourceItemAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(CertificationVehicle, CertificationVehicleAdmin)
admin.site.register(PassVehicle, PassVehicleAdmin)
