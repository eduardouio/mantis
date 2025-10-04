from django.http import JsonResponse
from django.views import View
from django.db.models import Q
from equipment.models import ResourceItem


class ResourcesAvailableAPI(View):
    """Listar recursos disponibles para asignar a un proyecto.

    Retorna recursos que:
        - Estén activos (is_active=True)
        - Tengan estado de disponibilidad DISPONIBLE
        - No sean servicios (type_equipment != 'SERVIC')
    """

    def get(self, request):
        """Obtener lista de recursos disponibles."""
        try:
            # Filtros base: Solo equipos disponibles y activos
            filters = Q(
                is_active=True,
                stst_status_disponibility='DISPONIBLE'
            )

            # Filtro por tipo de equipo (opcional)
            type_equipment = request.GET.get('type_equipment')
            if type_equipment:
                filters &= Q(type_equipment=type_equipment)

            # Filtro por estado del equipo (opcional)
            status_equipment = request.GET.get('status_equipment')
            if status_equipment:
                filters &= Q(stst_status_equipment=status_equipment)

            # Filtro por búsqueda de texto (código o nombre)
            search = request.GET.get('search')
            if search:
                filters &= (
                    Q(code__icontains=search) |
                    Q(name__icontains=search)
                )

            # Excluir servicios por defecto
            # (solo mostrar equipos físicos)
            exclude_services = request.GET.get(
                'exclude_services', 'true'
            ).lower() == 'true'
            if exclude_services:
                # Excluir servicios usando ~Q (negación)
                filters &= ~Q(type_equipment='SERVIC')

            # Obtener recursos
            resources = ResourceItem.objects.filter(filters).order_by(
                'type_equipment', 'code'
            )

            # Serializar
            data = [self._serialize(r) for r in resources]

            return JsonResponse({
                'success': True,
                'count': len(data),
                'data': data
            })

        except Exception as e:  # pragma: no cover
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def _serialize(self, resource):
        """Serializar ResourceItem a JSON."""
        return {
            'id': resource.id,
            'code': resource.code,
            'name': resource.name,
            'type_equipment': resource.type_equipment,
            'type_equipment_display': resource.get_type_equipment_display()
            if resource.type_equipment else None,
            'brand': resource.brand,
            'model': resource.model,
            'status_equipment': resource.stst_status_equipment,
            'status_disponibility': resource.stst_status_disponibility,
            'current_location': resource.stst_current_location,
            'capacity_gallons': (
                str(resource.capacity_gallons)
                if resource.capacity_gallons else None
            ),
        }
