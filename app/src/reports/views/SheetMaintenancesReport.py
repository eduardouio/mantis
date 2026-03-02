from django.views.generic import TemplateView
from projects.models.SheetMaintenance import SheetMaintenance
from common.AppLoggin import loggin_event


class SheetMaintenancesReportView(TemplateView):
    template_name = "reports/sheet_maintenances_report.html"

    STATUS_CHOICES = dict(SheetMaintenance._meta.get_field('status').choices)
    TYPE_CHOICES = dict(SheetMaintenance._meta.get_field('maintenance_type').choices)

    def get_context_data(self, **kwargs):
        loggin_event("Generando reporte de hojas de mantenimiento")
        context = super().get_context_data(**kwargs)

        sheets = SheetMaintenance.objects.filter(
            is_active=True,
            is_deleted=False,
        ).select_related(
            'id_sheet_project',
            'id_sheet_project__project',
            'id_sheet_project__project__partner',
            'responsible_technical',
            'resource_item',
        ).order_by('-start_date', '-sheet_number')

        all_sheets_list = []

        stats = {
            'total': 0,
            'total_cost': 0,
            'total_cost_logistics': 0,
            'total_days': 0,
            'with_pdf': 0,
            'without_pdf': 0,
            'by_status': {
                'DRAFT': {'count': 0, 'label': 'Borrador'},
                'CLOSED': {'count': 0, 'label': 'En Planilla'},
                'VOID': {'count': 0, 'label': 'Anulado'},
            },
            'by_type': {
                'PREVENTIVO': {'count': 0, 'label': 'Preventivo'},
                'CORRECTIVO': {'count': 0, 'label': 'Correctivo'},
            },
        }

        for sheet in sheets:
            has_pdf = bool(
                sheet.maintenance_file and sheet.maintenance_file.name
            )

            if has_pdf:
                stats['with_pdf'] += 1
            else:
                stats['without_pdf'] += 1

            stats['total'] += 1
            stats['total_cost'] += float(sheet.cost_total or 0)
            stats['total_cost_logistics'] += float(sheet.cost_logistics or 0)
            stats['total_days'] += int(sheet.total_days or 0)

            status_key = sheet.status
            if status_key in stats['by_status']:
                stats['by_status'][status_key]['count'] += 1

            type_key = sheet.maintenance_type
            if type_key in stats['by_type']:
                stats['by_type'][type_key]['count'] += 1

            sheet_project = sheet.id_sheet_project
            project = sheet_project.project if sheet_project else None
            partner = project.partner if project else None

            equipment_name = '-'
            if sheet.resource_item:
                equipment_name = str(sheet.resource_item)

            technical_name = '-'
            if sheet.responsible_technical:
                technical_name = str(sheet.responsible_technical)

            sheet_data = {
                'sheet': sheet,
                'sheet_number': sheet.sheet_number,
                'sheet_number_display': f"{sheet.sheet_number:06d}" if sheet.sheet_number else '-',
                'maintenance_type': sheet.maintenance_type,
                'type_display': self.TYPE_CHOICES.get(sheet.maintenance_type, sheet.maintenance_type),
                'start_date': sheet.start_date,
                'end_date': sheet.end_date,
                'total_days': sheet.total_days or 0,
                'cost_day': sheet.cost_day or 0,
                'cost_total': sheet.cost_total or 0,
                'cost_logistics': sheet.cost_logistics or 0,
                'location': sheet.location or '-',
                'rig': sheet.rig or '-',
                'code': sheet.code or '-',
                'equipment_name': equipment_name,
                'technical_name': technical_name,
                'requested_by': sheet.requested_by or '-',
                'performed_by': sheet.performed_by or '-',
                'approved_by': sheet.approved_by or '-',
                'maintenance_description': sheet.maintenance_description or '',
                'fault_description': sheet.fault_description or '',
                'observations': sheet.observations or '',
                'status': sheet.status,
                'status_display': self.STATUS_CHOICES.get(sheet.status, sheet.status),
                'partner_name': partner.name if partner else '-',
                'project_id': project.id if project else None,
                'project_location': project.location if project else '-',
                'series_code': sheet_project.series_code if sheet_project else '-',
                'sheet_project_id': sheet_project.id if sheet_project else None,
                'notes': sheet.notes or '',
                'has_pdf': has_pdf,
                'pdf_url': sheet.maintenance_file.url if has_pdf else None,
            }

            all_sheets_list.append(sheet_data)

        stats['total_cost_display'] = f"{stats['total_cost']:,.2f}"
        stats['total_cost_logistics_display'] = f"{stats['total_cost_logistics']:,.2f}"

        context.update({
            'all_sheets': all_sheets_list,
            'stats': stats,
        })

        return context
