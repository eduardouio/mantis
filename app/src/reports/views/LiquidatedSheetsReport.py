from django.views.generic import TemplateView
from projects.models.SheetProject import SheetProject
from projects.models.CustodyChain import CustodyChain
from common.AppLoggin import loggin_event


class LiquidatedSheetsReportView(TemplateView):
    template_name = "reports/liquidated_sheets_report.html"

    STATUS_CHOICES = dict(SheetProject._meta.get_field('status').choices)

    def get_context_data(self, **kwargs):
        loggin_event("Generando reporte de planillas por estado")
        context = super().get_context_data(**kwargs)

        sheets = SheetProject.objects.filter(
            is_active=True,
            is_deleted=False,
        ).select_related(
            'project',
            'project__partner',
        ).order_by('-period_start')

        all_sheets_list = []

        stats = {
            'total': 0,
            'total_amount': 0,
            'with_all_pdfs': 0,
            'missing_pdfs': 0,
            'by_status': {
                'IN_PROGRESS': {'count': 0, 'amount': 0, 'label': 'En Ejecución'},
                'LIQUIDATED': {'count': 0, 'amount': 0, 'label': 'Liquidado'},
                'INVOICED': {'count': 0, 'amount': 0, 'label': 'Facturado'},
                'CANCELLED': {'count': 0, 'amount': 0, 'label': 'Cancelado'},
            },
        }

        for sheet in sheets:
            custody_chains = CustodyChain.objects.filter(
                sheet_project=sheet,
                is_active=True,
            ).order_by('activity_date', 'consecutive')

            custody_chains_list = []
            chains_total = custody_chains.count()
            chains_with_pdf = 0

            for chain in custody_chains:
                has_pdf = bool(chain.custody_chain_file and chain.custody_chain_file.name)
                if has_pdf:
                    chains_with_pdf += 1

                custody_chains_list.append({
                    'id': chain.id,
                    'consecutive': chain.consecutive,
                    'activity_date': chain.activity_date,
                    'location': chain.location,
                    'status': chain.status,
                    'status_display': chain.get_status_display(),
                    'total_gallons': chain.total_gallons,
                    'total_barrels': chain.total_barrels,
                    'total_cubic_meters': chain.total_cubic_meters,
                    'has_pdf': has_pdf,
                    'pdf_url': chain.custody_chain_file.url if has_pdf else None,
                })

            has_sheet_pdf = bool(sheet.sheet_project_file and sheet.sheet_project_file.name)
            has_certificate_pdf = bool(
                sheet.certificate_final_disposition_file
                and sheet.certificate_final_disposition_file.name
            )
            has_invoice_pdf = bool(sheet.invoice_file and sheet.invoice_file.name)

            all_pdfs_loaded = (
                has_sheet_pdf
                and (chains_total == 0 or chains_with_pdf == chains_total)
            )

            if all_pdfs_loaded:
                stats['with_all_pdfs'] += 1
            else:
                stats['missing_pdfs'] += 1

            stats['total'] += 1
            stats['total_amount'] += float(sheet.total or 0)

            status_key = sheet.status
            if status_key in stats['by_status']:
                stats['by_status'][status_key]['count'] += 1
                stats['by_status'][status_key]['amount'] += float(sheet.total or 0)

            sheet_data = {
                'sheet': sheet,
                'project': sheet.project,
                'partner_name': sheet.project.partner.name if sheet.project and sheet.project.partner else '-',
                'project_location': sheet.project.location if sheet.project else '-',
                'project_id': sheet.project.id if sheet.project else None,
                'series_code': sheet.series_code,
                'service_type': sheet.get_service_type_display(),
                'status': sheet.status,
                'status_display': dict(SheetProject._meta.get_field('status').choices).get(sheet.status, sheet.status),
                'period_start': sheet.period_start,
                'period_end': sheet.period_end,
                'issue_date': sheet.issue_date,
                'subtotal': sheet.subtotal,
                'tax_amount': sheet.tax_amount,
                'total': sheet.total,
                'is_closed': sheet.is_closed,
                'has_sheet_pdf': has_sheet_pdf,
                'sheet_pdf_url': sheet.sheet_project_file.url if has_sheet_pdf else None,
                'has_certificate_pdf': has_certificate_pdf,
                'certificate_pdf_url': (
                    sheet.certificate_final_disposition_file.url if has_certificate_pdf else None
                ),
                'custody_chains': custody_chains_list,
                'chains_total': chains_total,
                'chains_with_pdf': chains_with_pdf,
                'all_pdfs_loaded': all_pdfs_loaded,
                'has_invoice_pdf': has_invoice_pdf,
                'invoice_pdf_url': sheet.invoice_file.url if has_invoice_pdf else None,
                'invoice_reference': sheet.invoice_reference or '',
            }

            all_sheets_list.append(sheet_data)

        stats['total_amount_display'] = f"{stats['total_amount']:,.2f}"
        for key in stats['by_status']:
            stats['by_status'][key]['amount_display'] = f"{stats['by_status'][key]['amount']:,.2f}"

        context.update({
            'all_sheets': all_sheets_list,
            'stats': stats,
        })

        return context
