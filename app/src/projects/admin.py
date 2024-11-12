from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    WorkOrder,
    Partner,
    Project,
    ProjectResourceItem
)


class MantenanceAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'date',
        'tecnical',
        'project',
        'start_hour',
        'end_hour',
        'destination_site',
        'vehicle',
        'volume_transported'
    )
    search_fields = (
        'project__name',
        'tecnical__first_name',
        'tecnical__last_name',
        'vehicle__plate',
    )

class PartnerAdmin(SimpleHistoryAdmin):
    list_display = (
        'business_tax_id',
        'name',
        'address',
        'phone',
        'email',
        'name_contact'
    )

    search_fields = (
        'business_tax_id',
        'name',

        'email',
    )


class ProjectAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'project_name',
        'partner',
        'place',
        'start_date',
        'end_date',
        'is_active',
        'type_service'
    )

    search_fields = (
        'project_name',
        'partner__name',
        'place',
    )


class ProjectEquipmentsAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'project',
        'equipment',
        'cost_rent',
        'cost_manteinance',
        'mantenance_frequency',
        'start_date',
        'end_date',
    )


admin.site.register(WorkOrder, MantenanceAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectResourceItem, ProjectEquipmentsAdmin)
