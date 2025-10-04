from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project
from common.AllProjectData import AllProjectData


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'presentations/project_presentation.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle del Proyecto {}'.format(
            self.object.partner
        )
        context['title_page'] = 'Detalle del Proyecto {}'.format(
            self.object.partner
        )

        # Obtener todos los datos del proyecto
        project_data = AllProjectData(self.object.id)
        context['project_info'] = project_data.get_project_basic_info()
        context['assigned_equipment'] = project_data.get_assigned_equipment()
        context['project_sheets'] = project_data.get_all_sheets()
        
        # Calcular totales de equipos
        total_rent = sum(
            eq['rent_cost'] for eq in context['assigned_equipment']
        )
        total_maintenance = sum(
            eq['maintenance_cost'] for eq in context['assigned_equipment']
        )
        context['total_monthly_rent'] = total_rent
        context['total_monthly_maintenance'] = total_maintenance

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        context['project'] = self.object
        message = ''
        if context['action'] == 'created':
            message = 'El proyecto ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El proyecto ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = (
                'No es posible eliminar el proyecto. '
                'Existen dependencias.'
            )
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'

        context['message'] = message
        return context
