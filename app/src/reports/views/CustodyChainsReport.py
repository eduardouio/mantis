from django.views.generic import TemplateView
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from common.AppLoggin import loggin_event


class CustodyChainsReportView(TemplateView):
    template_name = "reports/custody_chains_report.html"

    def get_context_data(self, **kwargs):
        loggin_event("Generando reporte de cadenas de custodia")
        context = super().get_context_data(**kwargs)

        chains = CustodyChain.objects.filter(
            is_active=True,
            is_deleted=False,
        ).select_related(
            'sheet_project',
            'sheet_project__project',
            'sheet_project__project__partner',
            'technical',
            'vehicle',
        ).order_by('-activity_date', '-consecutive')

        all_chains_list = []

        stats = {
            'total': 0,
            'total_gallons': 0,
            'total_barrels': 0,
            'total_cubic_meters': 0,
            'with_pdf': 0,
            'without_pdf': 0,
            'by_status': {
                'DRAFT': {'count': 0, 'label': 'Borrador'},
                'CLOSE': {'count': 0, 'label': 'Cerrado'},
                'CANCELLED': {'count': 0, 'label': 'Cancelado'},
                'INVOICE': {'count': 0, 'label': 'Facturado'},
            },
        }

        for chain in chains:
            has_pdf = bool(chain.custody_chain_file and chain.custody_chain_file.name)

            if has_pdf:
                stats['with_pdf'] += 1
            else:
                stats['without_pdf'] += 1

            stats['total'] += 1
            stats['total_gallons'] += float(chain.total_gallons or 0)
            stats['total_barrels'] += float(chain.total_barrels or 0)
            stats['total_cubic_meters'] += float(chain.total_cubic_meters or 0)

            status_key = chain.status
            if status_key in stats['by_status']:
                stats['by_status'][status_key]['count'] += 1

            sheet = chain.sheet_project
            project = sheet.project if sheet else None
            partner = project.partner if project else None

            # Tipos de agua
            water_types = []
            if chain.black_water:
                water_types.append('Negras')
            if chain.grey_water:
                water_types.append('Grises')
            if chain.clean_water:
                water_types.append('Limpias')
            if chain.activated_sludge:
                water_types.append('Lodos')
            if chain.treated_wastewater:
                water_types.append('Tratadas')
            if chain.organic_grease:
                water_types.append('Grasa')

            # Contar detalles
            details_count = ChainCustodyDetail.objects.filter(
                custody_chain=chain,
                is_active=True,
            ).count()

            chain_data = {
                'chain': chain,
                'consecutive': chain.consecutive or '-',
                'activity_date': chain.activity_date,
                'location': chain.location or '-',
                'status': chain.status,
                'status_display': chain.get_status_display(),
                'series_code': sheet.series_code if sheet else '-',
                'sheet_id': sheet.id if sheet else None,
                'partner_name': partner.name if partner else '-',
                'project_location': project.location if project else '-',
                'technical_name': str(chain.technical) if chain.technical else '-',
                'vehicle_plate': chain.vehicle.no_plate if chain.vehicle else '-',
                'start_time': chain.start_time,
                'end_time': chain.end_time,
                'time_duration': chain.time_duration,
                'total_gallons': chain.total_gallons,
                'total_barrels': chain.total_barrels,
                'total_cubic_meters': chain.total_cubic_meters,
                'have_logistic': chain.have_logistic,
                'water_types': ', '.join(water_types) if water_types else '-',
                'details_count': details_count,
                'contact_name': chain.contact_name or '-',
                'driver_name': chain.driver_name or '-',
                'has_pdf': has_pdf,
                'pdf_url': chain.custody_chain_file.url if has_pdf else None,
            }

            all_chains_list.append(chain_data)

        stats['total_gallons_display'] = f"{stats['total_gallons']:,.2f}"
        stats['total_barrels_display'] = f"{stats['total_barrels']:,.2f}"
        stats['total_cubic_meters_display'] = f"{stats['total_cubic_meters']:,.2f}"

        context.update({
            'all_chains': all_chains_list,
            'stats': stats,
        })

        return context
