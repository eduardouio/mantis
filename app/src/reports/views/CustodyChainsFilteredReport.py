from django.views.generic import TemplateView
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.Project import Project
from projects.models.Partner import Partner
from common.AppLoggin import loggin_event
from datetime import datetime


class CustodyChainsFilteredReportView(TemplateView):
    template_name = "reports/custody_chains_filtered_report.html"

    def get_context_data(self, **kwargs):
        loggin_event("Generando reporte filtrado de cadenas de custodia")
        context = super().get_context_data(**kwargs)

        # Obtener parámetros de filtro desde GET
        partner_id = self.request.GET.get('partner_id', '')
        project_id = self.request.GET.get('project_id', '')
        status_filter = self.request.GET.get('status', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        water_type = self.request.GET.get('water_type', '')
        has_pdf_filter = self.request.GET.get('has_pdf', '')
        series_code = self.request.GET.get('series_code', '')

        # Query base
        chains = CustodyChain.objects.filter(
            is_active=True,
            is_deleted=False,
        ).select_related(
            'sheet_project',
            'sheet_project__project',
            'sheet_project__project__partner',
            'technical',
            'vehicle',
        )

        # Aplicar filtros
        if partner_id:
            chains = chains.filter(sheet_project__project__partner_id=partner_id)

        if project_id:
            chains = chains.filter(sheet_project__project_id=project_id)

        if status_filter:
            chains = chains.filter(status=status_filter)

        if date_from:
            try:
                date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
                chains = chains.filter(activity_date__gte=date_from_parsed)
            except ValueError:
                pass

        if date_to:
            try:
                date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
                chains = chains.filter(activity_date__lte=date_to_parsed)
            except ValueError:
                pass

        if water_type:
            water_type_filters = {
                'black_water': {'black_water': True},
                'grey_water': {'grey_water': True},
                'clean_water': {'clean_water': True},
                'activated_sludge': {'activated_sludge': True},
                'treated_wastewater': {'treated_wastewater': True},
                'organic_grease': {'organic_grease': True},
            }
            if water_type in water_type_filters:
                chains = chains.filter(**water_type_filters[water_type])

        if series_code:
            chains = chains.filter(sheet_project__series_code__icontains=series_code)

        chains = chains.order_by('-activity_date', '-consecutive')

        # Filtro de PDF (post-query ya que es un FileField)
        all_chains_list = []

        stats = {
            'total': 0,
            'total_gallons': 0,
            'total_barrels': 0,
            'total_cubic_meters': 0,
            'total_hours': 0,
            'with_pdf': 0,
            'without_pdf': 0,
            'by_status': {
                'DRAFT': {'count': 0, 'label': 'Borrador'},
                'CLOSE': {'count': 0, 'label': 'Cerrado'},
                'CANCELLED': {'count': 0, 'label': 'Cancelado'},
                'INVOICE': {'count': 0, 'label': 'Facturado'},
            },
            'by_water_type': {
                'black_water': {'count': 0, 'label': 'Aguas Negras'},
                'grey_water': {'count': 0, 'label': 'Aguas Grises'},
                'clean_water': {'count': 0, 'label': 'Aguas Limpias'},
                'activated_sludge': {'count': 0, 'label': 'Lodos Activados'},
                'treated_wastewater': {'count': 0, 'label': 'Aguas Tratadas'},
                'organic_grease': {'count': 0, 'label': 'Grasa Orgánica'},
            },
        }

        for chain in chains:
            has_pdf = bool(chain.custody_chain_file and chain.custody_chain_file.name)

            # Filtro de PDF si se solicitó
            if has_pdf_filter == 'yes' and not has_pdf:
                continue
            elif has_pdf_filter == 'no' and has_pdf:
                continue

            if has_pdf:
                stats['with_pdf'] += 1
            else:
                stats['without_pdf'] += 1

            stats['total'] += 1
            stats['total_gallons'] += float(chain.total_gallons or 0)
            stats['total_barrels'] += float(chain.total_barrels or 0)
            stats['total_cubic_meters'] += float(chain.total_cubic_meters or 0)
            stats['total_hours'] += float(chain.time_duration or 0)

            status_key = chain.status
            if status_key in stats['by_status']:
                stats['by_status'][status_key]['count'] += 1

            # Conteo por tipo de agua
            if chain.black_water:
                stats['by_water_type']['black_water']['count'] += 1
            if chain.grey_water:
                stats['by_water_type']['grey_water']['count'] += 1
            if chain.clean_water:
                stats['by_water_type']['clean_water']['count'] += 1
            if chain.activated_sludge:
                stats['by_water_type']['activated_sludge']['count'] += 1
            if chain.treated_wastewater:
                stats['by_water_type']['treated_wastewater']['count'] += 1
            if chain.organic_grease:
                stats['by_water_type']['organic_grease']['count'] += 1

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

            # Contar detalles (equipos)
            details_count = ChainCustodyDetail.objects.filter(
                custody_chain=chain,
                is_active=True,
            ).count()

            # Calcular horas
            time_duration_hours = None
            if chain.time_duration:
                time_duration_hours = round(float(chain.time_duration) / 60, 2)

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
                'partner_id': partner.id if partner else None,
                'project_id': project.id if project else None,
                'project_location': project.location if project else '-',
                'technical_name': str(chain.technical) if chain.technical else '-',
                'vehicle_plate': chain.vehicle.plate if chain.vehicle else '-',
                'start_time': chain.start_time,
                'end_time': chain.end_time,
                'time_duration': chain.time_duration,
                'time_duration_hours': time_duration_hours,
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

        # Formatear totales
        stats['total_gallons_display'] = f"{stats['total_gallons']:,.2f}"
        stats['total_barrels_display'] = f"{stats['total_barrels']:,.2f}"
        stats['total_cubic_meters_display'] = f"{stats['total_cubic_meters']:,.2f}"
        stats['total_hours_display'] = f"{stats['total_hours']:,.2f}"

        # Obtener listas para los filtros (selectores)
        partners = Partner.objects.filter(
            is_active=True,
            is_deleted=False,
        ).order_by('name')

        projects = Project.objects.filter(
            is_active=True,
            is_deleted=False,
        ).select_related('partner').order_by('-id')

        # Verificar si hay filtros activos
        has_filters = any([
            partner_id, project_id, status_filter,
            date_from, date_to, water_type,
            has_pdf_filter, series_code,
        ])

        context.update({
            'all_chains': all_chains_list,
            'stats': stats,
            'partners': partners,
            'projects': projects,
            # Filtros actuales (para mantener estado en el formulario)
            'current_filters': {
                'partner_id': partner_id,
                'project_id': project_id,
                'status': status_filter,
                'date_from': date_from,
                'date_to': date_to,
                'water_type': water_type,
                'has_pdf': has_pdf_filter,
                'series_code': series_code,
            },
            'has_filters': has_filters,
        })

        return context
