from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Equipment, Vehicle, Supplie, SupplieStockMovment


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


class SupplieAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'min_stock',
        'max_stock',
    )

    search_fields = (
        'name',
        'description',
    )


class SupplieStockMovmentAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'supplie',
        'mantenance',
        'quantity',
        'type_movment',
        'date',
    )


admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Supplie, SupplieAdmin)
admin.site.register(SupplieStockMovment, SupplieStockMovmentAdmin)
