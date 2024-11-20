from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    WorkOrder,
    WorkOrderDetail,
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


class ProjectResourceItemAdmin(SimpleHistoryAdmin):
    pass


class WorkOrderAdmin(SimpleHistoryAdmin):
    pass


class WorkOrderDetailAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(WorkOrder, WorkOrderAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectResourceItem, ProjectResourceItemAdmin)
admin.site.register(WorkOrderDetail, WorkOrderDetailAdmin)
