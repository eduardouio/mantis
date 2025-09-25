from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Partner, Project
from common.PartnerCompleteInfo import PartnerCompleteInfo


class PartnerDetailView(LoginRequiredMixin, DetailView):
    model = Partner
    template_name = 'presentations/partner_presentation.html'
    context_object_name = 'partner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle del Socio de Negocio {}'.format(
            self.object.business_tax_id
        )
        context['title_page'] = 'Detalle del Socio de Negocio {}'.format(
            self.object.business_tax_id
        )
        
        # Agregar proyectos asociados al contexto
        projects = Project.objects.filter(
            partner=self.object,
            is_active=True
        ).order_by('-created_at')
        
        context['projects'] = projects
        
        # Agregar estadísticas de proyectos
        context['projects_stats'] = {
            'total': projects.count(),
            'active': projects.filter(is_closed=False, is_active=True).count(),
            'closed': projects.filter(is_closed=True).count(),
            'inactive': projects.filter(
                is_active=False, is_closed=False
            ).count(),
        }

        # Agregar información completa del partner
        try:
            partner_complete_info = PartnerCompleteInfo(self.object.id)
            context['partner_complete_info'] = partner_complete_info.get_complete_information()
        except Exception as e:
            # En caso de error, proporcionar datos por defecto
            context['partner_complete_info'] = {
                'projects_summary': {'total_projects': 0, 'active_projects': 0, 'closed_projects': 0},
                'financial_summary': {
                    'total_business_value': 0, 'total_rent_costs': 0, 'total_maintenance_costs': 0,
                    'total_invoiced_amount': 0, 'total_pending_amount': 0, 'average_project_value': 0,
                    'invoiced_sheets_count': 0, 'pending_sheets_count': 0, 'cancelled_sheets_count': 0
                },
                'operational_statistics': {
                    'active_equipment_count': 0, 'total_equipment_assigned': 0, 'retired_equipment_count': 0,
                    'average_project_duration': 0, 'equipment_utilization_rate': 0, 'most_used_equipment_type': 'N/A',
                    'equipment_by_type': []
                },
                'maintenance_alerts': [],
                'recent_activity': [],
                'partner_basic_info': {
                    'created_at': self.object.created_at,
                    'updated_at': self.object.updated_at,
                    'is_active': self.object.is_active
                }
            }
            # Log del error para debugging (opcional)
            print(f"Error obteniendo información completa del partner {self.object.id}: {str(e)}")

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        context['partner'] = self.object
        message = ''
        if context['action'] == 'created':
            message = 'El socio de negocio ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El socio de negocio ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = (
                'No es posible eliminar el socio de negocio. '
                'Existen dependencias.'
            )
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'

        context['message'] = message
        return context
