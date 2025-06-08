from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from equipment.models import ResourceItem
from projects.models import ProjectResourceItem


class ResourceItemDetailView(LoginRequiredMixin, DetailView):
    model = ResourceItem
    template_name = 'presentations/equipment_presentation.html'
    context_object_name = 'equipment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment = self.object
        today = timezone.now().date()
        
        # Información básica
        context['title_section'] = f'Ficha de Equipo - {equipment.name}'
        context['title_page'] = f'Ficha de Equipo - {equipment.name}'
        context['today'] = today
        
        # Obtener el parámetro de acción de la URL
        context['action'] = self.request.GET.get('action', None)
        
        # Estadísticas de uso del equipo
        context.update(self._get_equipment_statistics(equipment))
        
        # Información de proyectos asociados
        context.update(self._get_project_information(equipment))
        
        # Información de estado y mantenimiento
        context.update(self._get_maintenance_information(equipment))
        
        # Metadatos del sistema
        context.update(self._get_system_metadata(equipment))
        
        return context

    def _get_equipment_statistics(self, equipment):
        """Obtener estadísticas del equipo"""
        project_assignments = ProjectResourceItem.objects.filter(resource_item=equipment)
        active_assignments = project_assignments.filter(is_active=True)
        
        # Calcular estadísticas
        total_projects = project_assignments.count()
        active_projects = active_assignments.count()
        total_cost = sum(assignment.cost for assignment in project_assignments if assignment.cost)
        total_maintenance_cost = sum(assignment.cost_manteinance for assignment in project_assignments if assignment.cost_manteinance)
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'historical_projects': total_projects - active_projects,
            'total_revenue': total_cost + total_maintenance_cost,
            'total_cost': total_cost,
            'total_maintenance_cost': total_maintenance_cost,
        }

    def _get_project_information(self, equipment):
        """Obtener información de proyectos asociados"""
        project_assignments = ProjectResourceItem.objects.filter(
            resource_item=equipment
        ).select_related('project', 'project__partner').order_by('-start_date')
        
        current_assignment = project_assignments.filter(is_active=True).first()
        recent_assignments = project_assignments[:5]  # Últimos 5 proyectos
        
        return {
            'current_assignment': current_assignment,
            'recent_assignments': recent_assignments,
            'project_assignments': project_assignments,
        }

    def _get_maintenance_information(self, equipment):
        """Obtener información de mantenimiento y estado"""
        today = timezone.now().date()
        
        # Verificar si hay información de mantenimiento programado
        active_assignments = ProjectResourceItem.objects.filter(
            resource_item=equipment,
            is_active=True
        )
        
        maintenance_alerts = []
        for assignment in active_assignments:
            if assignment.end_date:
                days_until_end = (assignment.end_date - today).days
                if days_until_end <= 30:
                    maintenance_alerts.append({
                        'type': 'end_project',
                        'message': f'Proyecto termina en {days_until_end} días',
                        'project': assignment.project.partner.name if assignment.project and assignment.project.partner else 'Proyecto sin nombre',
                        'class': 'text-orange-600' if days_until_end > 7 else 'text-red-600'
                    })
        
        # Estado del equipo
        status_info = {
            'status_class': self._get_status_class(equipment.status),
            'needs_attention': equipment.status in ['EN REPARACION', 'DANADO', 'BUSCAR'],
            'is_available': equipment.status in ['DISPONIBLE', 'LIBRE'],
        }
        
        return {
            'maintenance_alerts': maintenance_alerts,
            'status_info': status_info,
        }

    def _get_status_class(self, status):
        """Obtener clase CSS según el estado del equipo"""
        status_classes = {
            'DISPONIBLE': 'text-green-600',
            'LIBRE': 'text-green-600',
            'RENTADO': 'text-blue-600',
            'EN REPARACION': 'text-red-600',
            'DANADO': 'text-red-600',
            'BUSCAR': 'text-orange-600',
            'INDEFINIDO': 'text-gray-600',
            'STAND BY': 'text-yellow-600',
            'EN ALMACEN': 'text-gray-600',
        }
        return status_classes.get(status, 'text-gray-600')

    def _get_system_metadata(self, equipment):
        """Obtener metadatos del sistema"""
        return {
            'created_info': {
                'date': equipment.created_at,
                'user': equipment.get_create_user(), # Usar el método de BaseModel
            },
            'updated_info': {
                'date': equipment.updated_at,
                'user': equipment.get_update_user(), # Usar el método de BaseModel
            },
            'system_info': {
                'version': getattr(equipment, 'version', '1.0'),
                'last_sync': getattr(equipment, 'last_sync', None),
                'system_notes': getattr(equipment, 'system_notes', None),
            }
        }
