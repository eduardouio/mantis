from django.views.generic import TemplateView
from projects.models.ShippingGuide import ShippingGuide, ShippingGuideDetail
from common.AppLoggin import loggin_event


class ShippingGuidesReportView(TemplateView):
    template_name = "reports/shipping_guides_report.html"

    STATUS_CHOICES = dict(ShippingGuide._meta.get_field('status').choices)
    TYPE_CHOICES = dict(ShippingGuide._meta.get_field('type_shipping_guide').choices)
    REASON_CHOICES = dict(ShippingGuide._meta.get_field('reason_transport').choices)

    def get_context_data(self, **kwargs):
        loggin_event("Generando reporte de guías de remisión")
        context = super().get_context_data(**kwargs)

        guides = ShippingGuide.objects.filter(
            is_active=True,
            is_deleted=False,
        ).select_related(
            'project',
            'project__partner',
        ).order_by('-issue_date', '-guide_number')

        all_guides_list = []

        stats = {
            'total': 0,
            'total_cost_transport': 0,
            'total_cost_stowage': 0,
            'with_pdf': 0,
            'without_pdf': 0,
            'by_status': {
                'DRAFT': {'count': 0, 'label': 'Borrador'},
                'CLOSED': {'count': 0, 'label': 'Cerrada'},
                'VOID': {'count': 0, 'label': 'Anulada'},
            },
            'by_type': {
                'EXIT': {'count': 0, 'label': 'Salida a Proyecto'},
                'IN': {'count': 0, 'label': 'Entrada a Base'},
                'TRANSFER': {'count': 0, 'label': 'Transferencia'},
            },
        }

        for guide in guides:
            has_pdf = bool(
                guide.shipping_guide_file and guide.shipping_guide_file.name
            )

            if has_pdf:
                stats['with_pdf'] += 1
            else:
                stats['without_pdf'] += 1

            stats['total'] += 1
            stats['total_cost_transport'] += float(guide.cost_transport or 0)
            stats['total_cost_stowage'] += float(guide.cost_stowage or 0)

            status_key = guide.status
            if status_key in stats['by_status']:
                stats['by_status'][status_key]['count'] += 1

            type_key = guide.type_shipping_guide
            if type_key in stats['by_type']:
                stats['by_type'][type_key]['count'] += 1

            project = guide.project
            partner = project.partner if project else None

            details_count = ShippingGuideDetail.objects.filter(
                shipping_guide=guide,
                is_active=True,
            ).count()

            guide_data = {
                'guide': guide,
                'guide_number': guide.guide_number,
                'guide_number_display': f"{guide.guide_number:07d}" if guide.guide_number else '-',
                'type_shipping_guide': guide.type_shipping_guide,
                'type_display': self.TYPE_CHOICES.get(guide.type_shipping_guide, guide.type_shipping_guide),
                'issue_date': guide.issue_date,
                'start_date': guide.start_date,
                'end_date': guide.end_date,
                'origin_place': guide.origin_place or '-',
                'destination_place': guide.destination_place or '-',
                'carrier_name': guide.carrier_name or '-',
                'carrier_ci': guide.carrier_ci or '-',
                'vehicle_plate': guide.vehicle_plate or '-',
                'dispatcher_name': guide.dispatcher_name or '-',
                'dispatcher_ci': guide.dispatcher_ci or '-',
                'contact_name': guide.contact_name or '-',
                'contact_phone': guide.contact_phone or '-',
                'recibed_by': guide.recibed_by or '-',
                'recibed_ci': guide.recibed_ci or '-',
                'reason_transport': guide.reason_transport or '-',
                'reason_display': self.REASON_CHOICES.get(guide.reason_transport, '-'),
                'cost_transport': guide.cost_transport or 0,
                'cost_stowage': guide.cost_stowage or 0,
                'status': guide.status,
                'status_display': self.STATUS_CHOICES.get(guide.status, guide.status),
                'partner_name': partner.name if partner else '-',
                'project_id': project.id if project else None,
                'project_location': project.location if project else '-',
                'details_count': details_count,
                'notes': guide.notes or '',
                'has_pdf': has_pdf,
                'pdf_url': guide.shipping_guide_file.url if has_pdf else None,
            }

            all_guides_list.append(guide_data)

        stats['total_cost_transport_display'] = f"{stats['total_cost_transport']:,.2f}"
        stats['total_cost_stowage_display'] = f"{stats['total_cost_stowage']:,.2f}"

        context.update({
            'all_guides': all_guides_list,
            'stats': stats,
        })

        return context
