from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Equipment, Vehicle, Supplie, SupplieStockMovment


class EquipmentAdmin(SimpleHistoryAdmin):
    pass


class VehicleAdmin(SimpleHistoryAdmin):
    pass


class SupplieAdmin(SimpleHistoryAdmin):
    pass


class SupplieStockMovmentAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Supplie, SupplieAdmin)
admin.site.register(SupplieStockMovment, SupplieStockMovmentAdmin)
