from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Equipment, Vehicle


class EquipmentAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'name',
        'brand',
        'model',
        'code',
        'date_purchase',
        'status'
    )

    search_fields = (
        'name',
        'brand',
        'model',
        'code',
        'status'
    )


class VehicleAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'no_plate',
        'model',
        'brand',
        'year',
        'type_vehicle',
    )    

    search_fields = (
        'no_plate',
        'brand',
        'model',
        'year',
        'type_vehicle',
    )


admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Vehicle, VehicleAdmin)
