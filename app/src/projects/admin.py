from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from projects.models import (
    Partner,
    Project,
    ProjectResourceItem,
    SheetProject,
    SheetProjectDetail,
    CustodyChain,
    ChainCustodyDetail,
    FinalDispositionCertificate,
    FinalDispositionCertificateDetail
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
        'id', 'partner', 'location', 'contact_name', 'contact_phone',
        'start_date', 'end_date', 'is_closed'
    )
    list_filter = (
        'partner', 'is_closed', 'is_active', 'start_date', 'end_date', 'created_at'
    )
    search_fields = (
        'location', 'contact_name', 'contact_phone', 'partner__name'
    )
    # readonly_fields heredado
    fieldsets = (
        ('Proyecto', {
            'fields': (
                'partner', 'location', 'contact_name', 'contact_phone',
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
        'project', 'resource_item', 'rent_cost', 'maintenance_cost',
        'maintenance_interval_days', 'operation_start_date',
        'operation_end_date', 'is_retired'
    )
    list_filter = (
        'project', 'resource_item', 'is_retired', 'is_active', 'operation_start_date', 'operation_end_date'
    )
    search_fields = (
        'project__partner__name', 'resource_item__name', 'resource_item__code'
    )
    # readonly heredado
    fieldsets = (
        ('Asignación', {
            'fields': (
                'project', 'resource_item', 'rent_cost', 'maintenance_cost',
                'maintenance_interval_days'
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


@admin.register(SheetProjectDetail)
class SheetProjectDetailAdmin(BaseModelAdmin):
    list_display = (
        'sheet_project', 'resource_item', 'detail', 'quantity', 'unit_price',
        'total_line', 'unit_measurement'
    )
    list_filter = (
        'sheet_project', 'resource_item', 'unit_measurement', 'is_active'
    )
    search_fields = (
        'sheet_project__project__partner__name', 'resource_item__name', 'detail'
    )
    # readonly heredado
    fieldsets = (
        ('Detalle', {
            'fields': (
                'sheet_project', 'resource_item', 'detail', 'item_unity',
                'quantity', 'unit_price', 'total_line', 'unit_measurement', 'is_active'
            )
        }),
        ('Notas', {'fields': ('notes',), 'classes': ('collapse',)}),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'id_user_created', 'id_user_updated'), 'classes': ('collapse',)
        })
    )


@admin.register(CustodyChain)
class CustodyChainAdmin(BaseModelAdmin):
    list_display = (
    'id', 'consecutive', 'technical', 'sheet_project',
    'activity_date', 'location', 'time_duration',
    'total_gallons', 'total_barrels', 'total_cubic_meters'
    )
    list_filter = (
        'technical', 'sheet_project', 'activity_date', 'is_active'
    )
    search_fields = (
        'consecutive',
        'technical__first_name', 'technical__last_name',
        'location'
    )
    # readonly heredado
    fieldsets = (
        ('Cadena', {
            'fields': (
                'technical', 'sheet_project', 'consecutive', 'activity_date',
                'location', 'start_time', 'end_time', 'time_duration'
            )
        }),
        ('Contacto', {
            'fields': (
                'contact_name', 'contact_position'
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


@admin.register(ChainCustodyDetail)
class ChainCustodyDetailAdmin(BaseModelAdmin):
    list_display = (
        'custody_chain', 'resource_item'
    )
    list_filter = (
        'custody_chain', 'resource_item', 'is_active'
    )
    search_fields = (
        'custody_chain__technical__first_name', 'resource_item__name'
    )
    # readonly heredado
    fieldsets = (
        ('Detalle', {
            'fields': (
                'custody_chain', 'resource_item', 'is_active'
            )
        }),
        ('Notas', {'fields': ('notes',), 'classes': ('collapse',)}),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'id_user_created', 'id_user_updated'), 'classes': ('collapse',)
        })
    )


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
