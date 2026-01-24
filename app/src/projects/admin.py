from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from projects.models import (
    Partner,
    Project,
    ProjectResourceItem,
    SheetProject,
    CustodyChain,
    ChainCustodyDetail,
    FinalDispositionCertificate,
    FinalDispositionCertificateDetail,
    ShippingGuide,
    ShippingGuideDetail
)


class BaseModelAdmin(SimpleHistoryAdmin):
    base_append_list_display = (
        'is_active', 'is_deleted', 'created_at', 'updated_at',
        'id_user_created', 'id_user_updated'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
    )

    def get_list_display(self, request):
        """Añade campos base al final sin duplicar."""
        base = list(getattr(self, 'list_display', ()))
        for f in self.base_append_list_display:
            if f not in base:
                base.append(f)
        return tuple(base)


@admin.register(Partner)
class PartnerAdmin(BaseModelAdmin):
    list_display = (
        'name', 'business_tax_id', 'email', 'phone'
    )
    search_fields = ('name', 'business_tax_id', 'email', 'phone')
    list_filter = ('is_active', 'created_at')
    # readonly_fields heredado de BaseModelAdmin
    fieldsets = (
        ('Datos Generales', {
            'fields': (
                'business_tax_id', 'name', 'email', 'phone', 'address',
                'name_contact', 'is_active'
            )
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
            ),
            'classes': ('collapse',)
        })
    )


@admin.register(Project)
class ProjectAdmin(BaseModelAdmin):
    list_display = (
        'id', 'partner', 'location', 'cardinal_point', 'contact_name', 'contact_phone',
        'start_date', 'end_date', 'is_closed'
    )
    list_filter = (
        'partner', 'is_closed', 'is_active', 'start_date', 'end_date', 'created_at'
    )
    search_fields = (
        'location', 'cardinal_point', 'contact_name', 'contact_phone', 'partner__name'
    )
    # readonly_fields heredado
    fieldsets = (
        ('Proyecto', {
            'fields': (
                'partner', 'location', 'cardinal_point', 'contact_name', 'contact_phone',
                'start_date', 'end_date', 'is_closed', 'is_active'
            )
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
            ),
            'classes': ('collapse',)
        })
    )


@admin.register(ProjectResourceItem)
class ProjectResourceItemAdmin(BaseModelAdmin):
    list_display = (
        'project', 'resource_item', 'cost', 'frequency_type',
        'interval_days', 'operation_start_date',
        'operation_end_date', 'is_retired'
    )
    list_filter = (
        'project', 'resource_item', 'frequency_type', 'is_retired', 'is_active', 'operation_start_date', 'operation_end_date'
    )
    search_fields = (
        'project__partner__name', 'resource_item__name', 'resource_item__code'
    )
    # readonly heredado
    fieldsets = (
        ('Asignación', {
            'fields': (
                'project', 'resource_item', 'detailed_description', 'cost',
                'frequency_type', 'interval_days', 'weekdays', 'monthdays'
            )
        }),
        ('Operación', {
            'fields': (
                'operation_start_date', 'operation_end_date', 'is_retired',
                'retirement_date', 'retirement_reason', 'is_active'
            )
        }),
        ('Notas', {
            'fields': ('notes',), 'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
            ), 'classes': ('collapse',)
        })
    )


@admin.register(SheetProject)
class SheetProjectAdmin(BaseModelAdmin):
    list_display = (
        'id', 'project', 'issue_date', 'period_start', 'period_end', 'status',
        'series_code', 'service_type', 'subtotal', 'tax_amount', 'total'
    )
    list_filter = (
        'project', 'status', 'period_start', 'period_end', 'issue_date', 'is_active'
    )
    search_fields = (
        'project__partner__name', 'series_code', 'service_type'
    )
    # readonly heredado
    fieldsets = (
        ('Período', {
            'fields': ('project', 'issue_date', 'period_start', 'period_end', 'status')
        }),
        ('Referencias', {
            'fields': (
                'series_code', 'service_type', 'client_po_reference',
                'contact_reference', 'contact_phone_reference',
                'final_disposition_reference', 'invoice_reference'
            ), 'classes': ('collapse',)
        }),
        ('Totales', {
            'fields': ('total_gallons', 'total_barrels', 'total_cubic_meters', 'subtotal', 'tax_amount', 'total')
        }),
        ('Notas', {
            'fields': ('notes',), 'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'id_user_created', 'id_user_updated'), 'classes': ('collapse',)
        })
    )


@admin.register(CustodyChain)
class CustodyChainAdmin(BaseModelAdmin):
    list_display = (
        'id', 'consecutive', 'get_sheet_project_id', 'get_project_id', 
        'technical', 'sheet_project', 'activity_date', 'location', 'issue_date', 
        'time_duration', 'total_gallons', 'total_barrels', 'total_cubic_meters'
    )
    list_filter = (
        'technical', 'sheet_project', 'activity_date', 'issue_date', 'is_active'
    )
    search_fields = (
        'consecutive',
        'technical__first_name', 'technical__last_name',
        'location', 'contact_name', 'driver_name'
    )
    # readonly heredado
    fieldsets = (
        ('Cadena', {
            'fields': (
                'technical', 'sheet_project', 'consecutive', 'activity_date',
                'location', 'issue_date', 'start_time', 'end_time', 'time_duration'
            )
        }),
        ('Contacto', {
            'fields': (
                'contact_name', 'dni_contact', 'contact_position', 'date_contact'
            ), 'classes': ('collapse',)
        }),
        ('Transportista', {
            'fields': (
                'driver_name', 'dni_driver', 'driver_position', 'driver_date'
            ), 'classes': ('collapse',)
        }),
        ('Volúmenes', {
            'fields': ('total_gallons', 'total_barrels', 'total_cubic_meters')
        }),
        ('Notas', {'fields': ('notes',), 'classes': ('collapse',)}),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
            ), 'classes': ('collapse',)
        })
    )

    def get_sheet_project_id(self, obj):
        return obj.sheet_project.id if obj.sheet_project else None
    get_sheet_project_id.short_description = 'ID Hoja'
    get_sheet_project_id.admin_order_field = 'sheet_project__id'

    def get_project_id(self, obj):
        return obj.sheet_project.project.id if obj.sheet_project and obj.sheet_project.project else None
    get_project_id.short_description = 'ID Proyecto'
    get_project_id.admin_order_field = 'sheet_project__project__id'


@admin.register(ChainCustodyDetail)
class ChainCustodyDetailAdmin(BaseModelAdmin):
    list_display = (
        'custody_chain', 'get_sheet_project_id', 'get_project_id', 'project_resource',
    )
    list_filter = (
        'custody_chain', 'custody_chain__sheet_project', 'custody_chain__sheet_project__project', 'project_resource', 'is_active'
    )
    search_fields = (
        'custody_chain__technical__first_name', 'project_resource__resource_item__name'
    )
    # readonly heredado
    fieldsets = (
        ('Detalle', {
            'fields': (
                'custody_chain', 'project_resource','is_active'
            )
        }),
        ('Notas', {'fields': ('notes',), 'classes': ('collapse',)}),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'id_user_created', 'id_user_updated'), 'classes': ('collapse',)
        })
    )

    def get_sheet_project_id(self, obj):
        return obj.custody_chain.sheet_project.id if obj.custody_chain and obj.custody_chain.sheet_project else None
    get_sheet_project_id.short_description = 'ID Hoja'
    get_sheet_project_id.admin_order_field = 'custody_chain__sheet_project__id'

    def get_project_id(self, obj):
        if obj.custody_chain and obj.custody_chain.sheet_project and obj.custody_chain.sheet_project.project:
            return obj.custody_chain.sheet_project.project.id
        return None
    get_project_id.short_description = 'ID Proyecto'
    get_project_id.admin_order_field = 'custody_chain__sheet_project__project__id'


@admin.register(FinalDispositionCertificate)
class FinalDispositionCertificateAdmin(BaseModelAdmin):
    list_display = (
        'nro_document', 'payment_sheet', 'date', 'total_bbl', 'total_gallons',
        'total_m3'
    )
    list_filter = (
        'payment_sheet', 'date', 'is_active'
    )
    search_fields = (
        'nro_document', 'payment_sheet__project__partner__name'
    )
    # readonly heredado
    fieldsets = (
        ('Certificado', {
            'fields': (
                'payment_sheet', 'nro_document', 'date',
                'text_document', 'is_active'
            )
        }),
        ('Totales', {
            'fields': ('total_bbl', 'total_gallons', 'total_m3')
        }),
        ('Notas', {'fields': ('notes',), 'classes': ('collapse',)}),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
            ), 'classes': ('collapse',)
        })
    )


@admin.register(FinalDispositionCertificateDetail)
class FinalDispositionCertificateDetailAdmin(BaseModelAdmin):
    list_display = (
        'final_disposition_certificate', 'custody_chain', 'detail',
        'quantity_bbl', 'quantity_gallons', 'quantity_m3'
    )
    list_filter = (
        'final_disposition_certificate', 'custody_chain', 'is_active'
    )
    search_fields = (
    'final_disposition_certificate__nro_document',
    'custody_chain__technical__first_name',
    'detail'
    )
    # readonly heredado
    fieldsets = (
        ('Detalle', {
            'fields': (
                'final_disposition_certificate', 'custody_chain', 'detail',
                'quantity_bbl', 'quantity_gallons', 'quantity_m3', 'is_active'
            )
        }),
        ('Notas', {'fields': ('notes',), 'classes': ('collapse',)}),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
            ), 'classes': ('collapse',)
        })
    )


@admin.register(ShippingGuide)
class ShippingGuideAdmin(BaseModelAdmin):
    list_display = (
        'id', 'guide_number', 'project', 'issue_date', 'start_date', 'end_date',
        'carrier_name', 'vehicle_plate'
    )
    list_filter = (
        'project', 'issue_date', 'start_date', 'end_date', 'is_active'
    )
    search_fields = (
        'guide_number', 'project__partner__name', 'carrier_name',
        'vehicle_plate', 'dispatcher_name', 'contact_name'
    )
    fieldsets = (
        ('Guía', {
            'fields': (
                'project', 'guide_number', 'issue_date', 'start_date', 'end_date',
                'origin_place', 'destination_place', 'is_active'
            )
        }),
        ('Transporte', {
            'fields': (
                'carrier_name', 'carrier_ci', 'vehicle_plate',
                'dispatcher_name', 'dispatcher_ci'
            )
        }),
        ('Contacto y Recepción', {
            'fields': (
                'contact_name', 'contact_phone', 'recibed_by', 'recibed_ci'
            ), 'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notes',), 'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
            ), 'classes': ('collapse',)
        })
    )


@admin.register(ShippingGuideDetail)
class ShippingGuideDetailAdmin(BaseModelAdmin):
    list_display = (
        'id', 'shipping_guide', 'description', 'quantity', 'unit'
    )
    list_filter = (
        'shipping_guide', 'is_active'
    )
    search_fields = (
        'shipping_guide__guide_number', 'description'
    )
    fieldsets = (
        ('Detalle', {
            'fields': (
                'shipping_guide', 'description', 'quantity', 'unit', 'is_active'
            )
        }),
        ('Notas', {
            'fields': ('notes',), 'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at', 'id_user_created', 'id_user_updated'
            ), 'classes': ('collapse',)
        })
    )
