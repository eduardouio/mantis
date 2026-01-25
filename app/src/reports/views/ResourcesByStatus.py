from django.views.generic import TemplateView
from equipment.models.ResourceItem import ResourceItem
from common.StatusResourceItem import StatusResourceItem
from common.AppLoggin import loggin_event


class ResourcesByStatusView(TemplateView):
    template_name = "reports/equipment_status_report.html"

    def get_context_data(self, **kwargs):
        loggin_event("Generando reporte de equipos por estado")
        context = super().get_context_data(**kwargs)

        # Obtener todos los equipos activos
        all_resources = ResourceItem.objects.filter(is_active=True, is_deleted=False)

        # Lista para todos los equipos con su estado
        all_equipment_list = []
        
        # Contadores por estado
        stats = {
            'total': 0,
            'disponible': 0,
            'rentado': 0,
            'danado': 0,
            'en_reparacion': 0,
            'incompleto': 0,
        }

        # Analizar cada equipo
        for resource in all_resources:
            status_checker = StatusResourceItem(resource)
            status_report = status_checker.get_status_report()
            
            # Determinar el estado principal del equipo
            availability = status_report.get('availability_status', 'DISPONIBLE')
            equipment_status = getattr(resource, 'stst_status_equipment', None)
            
            # Determinar el estado para la columna
            if equipment_status == 'DAÑADO':
                status_display = 'DAÑADO'
                status_class = 'danger'
                stats['danado'] += 1
            elif equipment_status == 'EN REPARACION':
                status_display = 'EN REPARACIÓN'
                status_class = 'warning'
                stats['en_reparacion'] += 1
            elif not status_report.get('is_complete', False):
                status_display = 'INCOMPLETO'
                status_class = 'secondary'
                stats['incompleto'] += 1
            elif availability == 'RENTADO':
                status_display = 'RENTADO'
                status_class = 'info'
                stats['rentado'] += 1
            else:
                status_display = 'DISPONIBLE'
                status_class = 'success'
                stats['disponible'] += 1
            
            stats['total'] += 1
            
            # Preparar datos del equipo
            equipment_data = {
                'resource': resource,
                'status_display': status_display,
                'status_class': status_class,
                'status_report': status_report,
                'is_complete': status_report.get('is_complete', False),
                'completion_percentage': status_report.get('completion_percentage', 0),
                'project_info': status_report.get('project_info'),
                'rental_info': status_report.get('rental_info'),
                'current_location': status_report.get('current_location'),
                'missing_items_count': len(status_report.get('missing_items', [])),
            }
            
            all_equipment_list.append(equipment_data)

        context.update({
            'all_equipment': all_equipment_list,
            'stats': stats,
        })

        return context
