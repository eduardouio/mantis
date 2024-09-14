from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Mantenance,
    ChainOfCustody,
    ChainOfCustodyPersonal,
    MantenanceSupplies,
    Partner,
    Project,
    ProjectEquipments
)


class MantenanceAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'date',
        'tecnical',
        'project',
        'authorized_by',
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


class ChainOfCustodyAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'date',
        'mantenance',
        'origin_location',
        'destination_location',
        'volume',
        'responsible',
        'vehicle',
        'nro_dni',
        'type_license',
        'check_by'
    )
    search_fields = (
        'mantenance__project__name',
        'mantenance__tecnical__first_name',
        'mantenance__tecnical__last_name',
        'mantenance__vehicle__plate',
    )


class ChainOfCustodyPersonalAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'date',
        'chain_of_custody',
        'name',
        'accion',
    )
    search_fields = (
        'chain_of_custody__mantenance__project__name',
        'chain_of_custody__mantenance__tecnical__first_name',
        'chain_of_custody__mantenance__tecnical__last_name',
        'chain_of_custody__mantenance__vehicle__plate',
    )


class MantenanceSuppliesAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'mantenance',
        'equipment',
        'make_vaccum',
        'make_cleaning',
        'use_chemical',
    )
    search_fields = (
        'mantenance__project__name',
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


admin.site.register(Mantenance, MantenanceAdmin)
admin.site.register(ChainOfCustody, ChainOfCustodyAdmin)
admin.site.register(MantenanceSupplies, MantenanceSuppliesAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ChainOfCustodyPersonal, ChainOfCustodyPersonalAdmin)
admin.site.register(ProjectEquipments, ProjectEquipmentsAdmin)
