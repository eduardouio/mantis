from django.http import JsonResponse
from django.views import View
from django.db.models import Q
from equipment.models import ResourceItem


class ResourcesAvailableAPI(View):
    """Listar recursos disponibles para asignar a un proyecto.

    Retorna recursos que:
        - Estén activos (is_active=True)
        - Tengan estado de disponibilidad DISPONIBLE
    """

    def get(self, request):
        """Obtener lista de recursos disponibles."""
        try:

            filters = Q(is_active=True, stst_status_disponibility="DISPONIBLE")

            resources = ResourceItem.objects.filter(filters).order_by(
                "type_equipment", "code"
            )

            data = [self._serialize(r) for r in resources]

            return JsonResponse({"success": True, "count": len(data), "data": data})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def _serialize(self, resource):
        """Serializar ResourceItem a JSON."""
        return {
            "id": resource.id,
            "code": resource.code,
            "name": resource.name,
            "type_equipment": resource.type_equipment,
            "type_equipment_display": (
                resource.get_type_equipment_display()
                if resource.type_equipment
                else None
            ),
            "brand": resource.brand,
            "model": resource.model,
            "status_equipment": resource.stst_status_equipment,
            "status_disponibility": resource.stst_status_disponibility,
            "current_location": resource.stst_current_location,
            "capacity_gallons": (
                str(resource.capacity_gallons) if resource.capacity_gallons else None
            ),
        }
