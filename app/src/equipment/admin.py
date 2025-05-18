from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import ResourceItem, Vehicle, CertificationVehicle


class EquipmentAdmin(SimpleHistoryAdmin):
    pass


class VehicleAdmin(SimpleHistoryAdmin):
    list_display = (
        'brand',
        'model',
        'type_vehicle',
        'no_plate',
    )

    list_filter = (
        'type_vehicle',
        'status_vehicle',
        'owner_transport',
    )

    search_fields = (
        'no_plate',
        'brand',
        'model',
        'year',
        'serial_number',
        'engine_number',
        'chassis_number'
    )
    ordering = ('-year',)


class CertificationVehicleAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'date_start',
        'date_end'
    )

    list_filter = (
        'name',
        'date_start',
        'date_end'
    )

    search_fields = (
        'name',
        'date_start',
        'date_end'
    )
    ordering = ('-date_start',)


admin.site.register(ResourceItem, EquipmentAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(CertificationVehicle, CertificationVehicleAdmin)
