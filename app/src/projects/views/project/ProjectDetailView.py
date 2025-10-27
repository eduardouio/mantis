from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project
from common.AllProjectData import AllProjectData
import json


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
        assigned_equipment_list = project_data.get_assigned_equipment()
        context['project_sheets'] = project_data.get_all_sheets()
        
        # Serializar equipos asignados para Vue
        assigned_equipment_json = []
        for eq in assigned_equipment_list:
            assigned_equipment_json.append({
                'assignment_id': eq.get('assignment_id'),
                'resource_id': eq.get('resource_id'),
                'resource_code': eq.get('resource_code'),
                'resource_name': eq.get('resource_name'),
                'is_service': eq.get('is_service', False),
                'status_disponibility': eq.get('status_disponibility'),
                'rent_cost': str(eq.get('rent_cost', 0)),
                'maintenance_cost': str(eq.get('maintenance_cost', 0)),
                'maintenance_interval_days': eq.get('maintenance_interval_days', 15),
                'operation_start_date': eq.get('operation_start_date'),
                'operation_end_date': eq.get('operation_end_date'),
                'is_retired': eq.get('is_retired', False)
            })
        
        context['assigned_equipment'] = json.dumps(assigned_equipment_json)
        
        # Calcular totales de equipos
        total_rent = sum(
            float(eq.get('rent_cost', 0)) for eq in assigned_equipment_list
        )
        total_maintenance = sum(
            float(eq.get('maintenance_cost', 0)) for eq in assigned_equipment_list
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
