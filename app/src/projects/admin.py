from django.contrib import admin
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Mantenance, ChainOfCustody, MantenanceSupplies, Partner, Project


class MantenanceAdmin(SimpleHistoryAdmin):
    pass


class ChainOfCustodyAdmin(SimpleHistoryAdmin):
    pass


class MantenanceSuppliesAdmin(SimpleHistoryAdmin):
    pass


class PartnerAdmin(SimpleHistoryAdmin):
    pass


class ProjectAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(Mantenance, MantenanceAdmin)
admin.site.register(ChainOfCustody, ChainOfCustodyAdmin)
admin.site.register(MantenanceSupplies, MantenanceSuppliesAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Project, ProjectAdmin)
