from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from equipment.models import ResourceItem, Vehicle, CertificationVehicle, PassVehicle


class ResourceItemAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'code',
        'type',
        'subtype',
        'brand',
        'model',
        'base_price',
        'status',
        'current_location',
        'capacity_display',
        'is_active',
        'created_at',
    )

    list_filter = (
        'type',
        'subtype',
        'status',
        'brand',
        'is_active',
        'created_at',
        'date_purchase',
        'plant_capacity',
    )

    search_fields = (
        'name',
        'code',
        'brand',
        'model',
        'serial_number',
        'current_location',
        'notes',
        'repair_reason',
    )

    ordering = ('-created_at', 'name')

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'type', 'subtype', 'brand', 'model', 'serial_number', 'date_purchase', 'base_price')
        }),
        ('Características Físicas', {
            'fields': ('height', 'width', 'depth', 'weight'),
            'classes': ('collapse',)
        }),
        ('Capacidad', {
            'fields': ('capacity_gallons', 'plant_capacity'),
            'classes': ('collapse',)
        }),
        ('Estado y Ubicación', {
            'fields': ('status', 'repair_reason', 'current_location', 'current_project_id', 'is_active')
        }),
        ('Fechas de Proyecto', {
            'fields': ('commitment_date', 'release_date'),
            'classes': ('collapse',)
        }),
        ('Características Lavamanos', {
            'fields': ('foot_pumps', 'sink_soap_dispenser', 'paper_towels'),
            'classes': ('collapse',)
        }),
        ('Características Baterías Sanitarias', {
            'fields': ('paper_dispenser', 'soap_dispenser', 'napkin_dispenser', 'urinals', 'seats', 'toilet_pump', 'sink_pump', 'toilet_lid', 'bathroom_bases', 'ventilation_pipe'),
            'classes': ('collapse',)
        }),
        ('Componentes Especiales - Blower', {
            'fields': ('blower_brand', 'blower_model', 'blower_pulley_brand', 'blower_pulley_model'),
            'classes': ('collapse',)
        }),
        ('Componentes Especiales - Motor', {
            'fields': ('engine_brand', 'engine_model', 'motor_pulley_brand', 'motor_pulley_model', 'motor_guard_brand', 'motor_guard_model'),
            'classes': ('collapse',)
        }),
        ('Componentes Especiales - Otros', {
            'fields': ('belt_brand', 'belt_model', 'belt_type', 'electrical_panel_brand', 'electrical_panel_model'),
            'classes': ('collapse',)
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

    readonly_fields = ('created_at', 'updated_at',
                       'id_user_created', 'id_user_updated', 'capacity_display')

    date_hierarchy = 'created_at'

    def capacity_display(self, obj):
        return obj.capacity_display
    capacity_display.short_description = 'Capacidad'


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
            'fields': ('serial_number', 'engine_number', 'chassis_number')
        }),
        ('Estado y Propietario', {
            'fields': ('status_vehicle', 'owner_transport', 'is_active')
        }),
        ('Fechas y Certificaciones', {
            'fields': ('date_matricula', 'due_date_matricula', 'due_date_cert_oper', 'date_mtop', 'date_technical_review')
        }),
        ('Información de Seguros', {
            'fields': ('nro_poliza', 'insurance_company', 'insurance_issue_date', 'insurance_expiration_date', 'duedate_satellite'),
            'classes': ('collapse',)
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

    readonly_fields = ('created_at', 'updated_at',
                       'id_user_created', 'id_user_updated')

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

    readonly_fields = ('created_at', 'updated_at',
                       'id_user_created', 'id_user_updated')

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

    readonly_fields = ('created_at', 'updated_at',
                       'id_user_created', 'id_user_updated')

    date_hierarchy = 'fecha_caducidad'

    def get_vehicle_plate(self, obj):
        return obj.vehicle.no_plate if obj.vehicle else 'N/A'
    get_vehicle_plate.short_description = 'Placa del Vehículo'


admin.site.register(ResourceItem, ResourceItemAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(CertificationVehicle, CertificationVehicleAdmin)
admin.site.register(PassVehicle, PassVehicleAdmin)
