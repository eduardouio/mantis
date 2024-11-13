from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    WorkOrder,
    Partner,
    Project,
    ProjectResourceItem
)


class MantenanceAdmin(SimpleHistoryAdmin):
    pass


class PartnerAdmin(SimpleHistoryAdmin):
    pass


class ProjectAdmin(SimpleHistoryAdmin):
    pass


class ProjectEquipmentsAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(WorkOrder, MantenanceAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectResourceItem, ProjectEquipmentsAdmin)
