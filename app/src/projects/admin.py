from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    WorkOrder,
    WorkOrderDetail,
    WorkOrderMaintenance,
    Partner,
    Project,
    ProjectResourceItem
)


class PartnerAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'business_tax_id',
        'email',
        'phone',
        'name_contact',
        'is_active',
        'created_at', 'updated_at',
    )

    list_filter = (
        'is_active',
        'created_at', 'updated_at',
    )

    search_fields = (
        'name',
        'business_tax_id',
        'email',
        'phone',
        'name_contact',
        'address',
        'notes',
    )

    ordering = ('-created_at', 'name')

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'business_tax_id', 'email', 'phone', 'address')
        }),
        ('Contacto', {
            'fields': ('name_contact',)
        }),
        ('Autorizaciones', {
            'fields': ('authorized_tehcnicals', 'authorized_vehicle'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created',
                'id_user_updated'
            ),
            'classes': ('collapse',)
        })
    )

    readonly_fields = (
        'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
    )
    date_hierarchy = 'created_at'


class ProjectAdmin(SimpleHistoryAdmin):
    list_display = (
        'get_project_name',
        'partner',
        'place',
        'start_date',
        'end_date',
        'is_closed',
        'is_active',
        'created_at', 'updated_at',
    )

    list_filter = (
        'partner',
        'is_closed',
        'is_active',
        'start_date',
        'end_date',
        'created_at',
    )

    search_fields = (
        'partner__name',
        'place',
        'avrebiature',
        'contact_name',
        'phone_contact',
        'TechnicalResponsible',
        'notes',
    )

    ordering = ('-start_date', '-created_at')

    fieldsets = (
        ('Información del Proyecto', {
            'fields': (
                'partner', 'place', 'avrebiature', 'TechnicalResponsible'
            )
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date', 'is_closed')
        }),
        ('Contacto', {
            'fields': ('contact_name', 'phone_contact')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created',
                'id_user_updated'
            ),
            'classes': ('collapse',)
        })
    )

    readonly_fields = (
        'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
    )
    date_hierarchy = 'start_date'

    def get_project_name(self, obj):
        return f"{obj.partner.name} - {obj.place or 'Sin lugar'}"
    get_project_name.short_description = 'Proyecto'


class ProjectResourceItemAdmin(SimpleHistoryAdmin):
    list_display = (
        'get_project_name',
        'get_resource_name',
        'cost',
        'start_date',
        'end_date',
        'retired_date',
        'is_active',
        'created_at', 'updated_at',
    )

    list_filter = (
        'project__partner',
        'mantenance_frequency',
        'is_active',
        'start_date',
        'end_date',
        'created_at',
    )

    search_fields = (
        'project__partner__name',
        'project__place',
        'resource_item__name',
        'resource_item__code',
        'motive_retired',
        'notes',
    )

    ordering = ('-start_date', '-created_at')

    fieldsets = (
        ('Asignación', {
            'fields': ('project', 'resource_item')
        }),
        ('Costos y Mantenimiento', {
            'fields': (
                'cost', 'cost_manteinance', 'mantenance_frequency',
                'times_mantenance'
            )
        }),
        ('Fechas de Operación', {
            'fields': ('start_date', 'end_date', 'retired_date')
        }),
        ('Retiro', {
            'fields': ('motive_retired',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created',
                'id_user_updated'
            ),
            'classes': ('collapse',)
        })
    )

    readonly_fields = (
        'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
    )
    date_hierarchy = 'start_date'

    def get_project_name(self, obj):
        partner_name = obj.project.partner.name
        place = obj.project.place or 'Sin lugar'
        return f"{partner_name} - {place}"
    get_project_name.short_description = 'Proyecto'

    def get_resource_name(self, obj):
        return f"{obj.resource_item.name} ({obj.resource_item.code})"
    get_resource_name.short_description = 'Recurso'


class WorkOrderAdmin(SimpleHistoryAdmin):
    list_display = (
        'work_order',
        'get_project_name',
        'tecnical',
        'date',
        'is_active',
        'created_at', 'updated_at',
    )

    list_filter = (
        'project__partner',
        'tecnical',
        'date',
        'is_active',
        'created_at',
    )

    search_fields = (
        'work_order',
        'project__partner__name',
        'project__place',
        'tecnical__user__first_name',
        'tecnical__user__last_name',
        'notes',
    )

    ordering = ('-date', '-created_at')

    fieldsets = (
        ('Información de la Orden', {
            'fields': ('work_order', 'project', 'tecnical', 'date')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created',
                'id_user_updated'
            ),
            'classes': ('collapse',)
        })
    )

    readonly_fields = (
        'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
    )
    date_hierarchy = 'date'

    def get_project_name(self, obj):
        return f"{obj.project.partner.name} - {obj.project.place or 'Sin lugar'}"
    get_project_name.short_description = 'Proyecto'


class WorkOrderDetailAdmin(SimpleHistoryAdmin):
    list_display = (
        'get_work_order',
        'get_resource_item',
        'type_service',
        'location',
        'start_hour',
        'total_hours',
        'cost',
        'is_active',
        'created_at', 'updated_at',
    )

    list_filter = (
        'type_service',
        'unit',
        'mat_transported_aguas_negras',
        'mat_transported_aguas_grises',
        'mat_transported_agua_limpa',
        'is_active',
        'start_hour',
        'created_at',
    )

    search_fields = (
        'work_order__work_order',
        'resource_item__resource_item__name',
        'location',
        'origin_site',
        'destination_site',
        'volume_transported',
        'notes',
    )

    ordering = ('-start_hour', '-created_at')

    fieldsets = (
        ('Información Básica', {
            'fields': ('work_order', 'resource_item', 'type_service', 'cost')
        }),
        ('Ubicación y Tiempo', {
            'fields': ('location', 'start_hour', 'end_hour', 'total_hours')
        }),
        ('Transporte', {
            'fields': (
                'origin_site', 'destination_site', 'volume_transported', 'unit'
            ),
            'classes': ('collapse',)
        }),
        ('Material Transportado', {
            'fields': (
                'mat_transported_aguas_negras', 'mat_transported_aguas_grises',
                'mat_transported_agua_limpa', 'mat_trasported_lodos_activos',
                'mat_trasported_agua_residual_tratada'
            ),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created',
                'id_user_updated'
            ),
            'classes': ('collapse',)
        })
    )

    readonly_fields = (
        'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
    )
    date_hierarchy = 'start_hour'

    def get_work_order(self, obj):
        return obj.work_order.work_order
    get_work_order.short_description = 'Orden de Trabajo'

    def get_resource_item(self, obj):
        # Mostrar nombre y código del recurso asociado
        name = obj.resource_item.resource_item.name
        code = obj.resource_item.resource_item.code
        return f"{name} ({code})"
    get_resource_item.short_description = 'Recurso'


class WorkOrderMaintenanceAdmin(SimpleHistoryAdmin):
    list_display = (
        'get_work_order',
        'work_vaccum',
        'work_cleaning',
        'use_chemical',
        'use_disinfectant',
        'is_active',
        'created_at', 'updated_at',
    )

    list_filter = (
        'work_vaccum',
        'work_cleaning',
        'use_chemical',
        'use_toilet_paper',
        'use_tz',
        'use_soap',
        'use_trash_bag',
        'use_disinfectant',
        'is_active',
        'created_at',
    )

    search_fields = (
        'work_order_detail__work_order__work_order',
        'work_order_detail__location',
        'notes',
    )

    ordering = ('-created_at',)

    fieldsets = (
        ('Detalle de Orden', {
            'fields': ('work_order_detail',)
        }),
        ('Trabajos Realizados', {
            'fields': ('work_vaccum', 'work_cleaning', 'use_chemical')
        }),
        ('Materiales Utilizados', {
            'fields': (
                'use_toilet_paper', 'use_tz', 'use_soap', 'use_trash_bag',
                'use_disinfectant'
            ),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created',
                'id_user_updated'
            ),
            'classes': ('collapse',)
        })
    )

    readonly_fields = (
        'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
    )
    date_hierarchy = 'created_at'

    def get_work_order(self, obj):
        return obj.work_order_detail.work_order.work_order
    get_work_order.short_description = 'Orden de Trabajo'


admin.site.register(Partner, PartnerAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectResourceItem, ProjectResourceItemAdmin)
admin.site.register(WorkOrder, WorkOrderAdmin)
admin.site.register(WorkOrderDetail, WorkOrderDetailAdmin)
admin.site.register(WorkOrderMaintenance, WorkOrderMaintenanceAdmin)
