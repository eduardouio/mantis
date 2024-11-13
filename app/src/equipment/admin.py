from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import ResourceItem, Vehicle


class EquipmentAdmin(SimpleHistoryAdmin):
    pass


class VehicleAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(ResourceItem, EquipmentAdmin)
admin.site.register(Vehicle, VehicleAdmin)
