from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from equipment.models import ResourceItem, Vehicle, CertificationVehicle, PassVehicle


class ResourceItemAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'code',
        'type_equipment',
        'brand',
        'model',
        'stst_status_equipment',
        'stst_status_disponibility',
        'stst_current_location',
        'is_active',
        'created_at',
    )

    list_filter = (
        'type_equipment',
        'stst_status_equipment',
        'stst_status_disponibility',
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
        'serial_number',
        'stst_current_location',
        'stst_repair_reason',
    )

    ordering = ('-created_at', 'name')

    fieldsets = (
        ('Información Básica', {
            'fields': (
                'name', 'code', 'type_equipment', 'brand', 'model', 
                'serial_number', 'date_purchase',
                'height', 'width', 'depth', 'weight',
                'capacity_gallons', 'plant_capacity'
            )
        }),
        ('Estado y Disponibilidad', {
            'fields': (
                'stst_status_equipment', 'stst_status_disponibility',
                'stst_repair_reason', 'stst_current_location',
                'stst_current_project_id', 'stst_commitment_date',
                'stst_release_date', 'is_active'
            )
        }),
        ('Características de Lavamanos', {
            'fields': (
                'have_foot_pumps', 'have_soap_dispenser', 'have_paper_towels'
            ),
            'classes': ('collapse',)
        }),
        ('Características de Baterías Sanitarias', {
            'fields': (
                'have_paper_dispenser', 'have_napkin_dispenser', 'have_urinals',
                'have_seat', 'have_toilet_pump', 'have_sink_pump',
                'have_toilet_lid', 'have_bathroom_bases', 'have_ventilation_pipe'
            ),
            'classes': ('collapse',)
        }),
        ('Componentes - Blower', {
            'fields': (
                'have_blower_brand', 'blower_brand', 'blower_model',
                'have_blower_pulley', 'blower_pulley_brand', 'blower_pulley_model'
            ),
            'classes': ('collapse',)
        }),
        ('Componentes - Motor', {
            'fields': (
                'have_engine', 'engine_brand', 'engine_model', 'engine_fases',
                'have_motor_pulley', 'motor_pulley_brand', 'motor_pulley_model',
                'have_motor_guard', 'engine_guard_brand', 'engine_guard_model'
            ),
            'classes': ('collapse',)
        }),
        ('Componentes - Bandas y Panel', {
            'fields': (
                'have_belt_brand', 'belt_brand', 'belt_model', 'belt_type',
                'have_electrical_panel', 'electrical_panel_brand', 'electrical_panel_model'
            ),
            'classes': ('collapse',)
        }),
        ('Componentes - Relés', {
            'fields': (
                'have_relay_engine', 'relay_engine',
                'have_relay_blower', 'relay_blower'
            ),
            'classes': ('collapse',)
        }),
        ('Componentes - Plantas de Tratamiento', {
            'fields': (
                'have_uv_filter', 'uv_filter',
                'have_pump_filter', 'pump_filter',
                'have_pump_pressure', 'pump_pressure',
                'have_pump_dosing', 'pump_dosing',
                'have_sand_carbon_filter', 'sand_carbon_filter',
                'have_hidroneumatic_tank', 'hidroneumatic_tank'
            ),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at',
                'id_user_created', 'id_user_updated'
            ),
            'classes': ('collapse',)
        })
    )

    readonly_fields = (
        'created_at', 'updated_at',
        'id_user_created', 'id_user_updated',
        'capacity_display'
    )

    date_hierarchy = 'created_at'

    def capacity_display(self, obj):
        return obj.capacity_display() if callable(getattr(obj, 'capacity_display', None)) else 'N/A'
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
            'fields': ('nro_poliza', 'insurance_company', 'insurance_issue_date', 'insurance_expiration_date', 'due_date_satellite'),
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
