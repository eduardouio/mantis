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

        # Agrupar equipos por estado
        equipment_by_status = {
            'DISPONIBLE': [],
            'RENTADO': [],
            'DAÑADO': [],
            'EN REPARACION': [],
            'INCOMPLETO': []
        }

        # Analizar cada equipo
        for resource in all_resources:
            status_checker = StatusResourceItem(resource)
            status_report = status_checker.get_status_report()
            
            # Determinar el estado principal del equipo
            availability = status_report.get('availability_status', 'DISPONIBLE')
            equipment_status = getattr(resource, 'stst_status_equipment', None)
            
            # Preparar datos del equipo
            equipment_data = {
                'resource': resource,
                'status_report': status_report,
                'is_complete': status_report.get('is_complete', False),
                'completion_percentage': status_report.get('completion_percentage', 0),
                'project_info': status_report.get('project_info'),
                'rental_info': status_report.get('rental_info'),
                'current_location': status_report.get('current_location'),
                'missing_items_count': len(status_report.get('missing_items', [])),
            }
            
            # Clasificar el equipo según su estado
            if equipment_status == 'DAÑADO':
                equipment_by_status['DAÑADO'].append(equipment_data)
            elif equipment_status == 'EN REPARACION':
                equipment_by_status['EN REPARACION'].append(equipment_data)
            elif not status_report.get('is_complete', False):
                equipment_by_status['INCOMPLETO'].append(equipment_data)
            elif availability == 'RENTADO':
                equipment_by_status['RENTADO'].append(equipment_data)
            else:
                equipment_by_status['DISPONIBLE'].append(equipment_data)

        # Calcular estadísticas
        total_equipments = all_resources.count()
        stats = {
            'total': total_equipments,
            'disponible': len(equipment_by_status['DISPONIBLE']),
            'rentado': len(equipment_by_status['RENTADO']),
            'danado': len(equipment_by_status['DAÑADO']),
            'en_reparacion': len(equipment_by_status['EN REPARACION']),
            'incompleto': len(equipment_by_status['INCOMPLETO']),
        }

        context.update({
            'equipment_disponible': equipment_by_status['DISPONIBLE'],
            'equipment_rentado': equipment_by_status['RENTADO'],
            'equipment_danado': equipment_by_status['DAÑADO'],
            'equipment_reparacion': equipment_by_status['EN REPARACION'],
            'equipment_incompleto': equipment_by_status['INCOMPLETO'],
            'stats': stats,
        })

        return context
