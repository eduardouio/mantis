from django.http import JsonResponse
from django.views import View
import json
from datetime import date

from common.EquipmentManager import EquipmentManager, EquipmentManagerError


class ReactivateResourceAPI(View):
    """API para verificar y reactivar recursos retirados en un proyecto."""

    def get(self, request):
        """
        Verifica si un recurso retirado puede ser reactivado.

        Query params:
            id (int): ID del ProjectResourceItem retirado.

        Returns:
            JSON con can_reactivate (bool), reason, y datos del recurso.
        """
        try:
            project_resource_id = request.GET.get("id")
            if not project_resource_id:
                return JsonResponse(
                    {"error": "El parámetro 'id' es requerido."}, status=400
                )

            result = EquipmentManager.check_reactivation(int(project_resource_id))
            return JsonResponse(result, status=200)

        except EquipmentManagerError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse(
                {"error": f"Error al verificar reactivación: {str(e)}"}, status=500
            )

    def put(self, request):
        """
        Reactiva un recurso previamente retirado en el mismo proyecto.

        Body JSON:
            id (int): ID del ProjectResourceItem retirado.
            new_start_date (str, opcional): Nueva fecha de inicio en formato
                YYYY-MM-DD. Si se omite se conserva la fecha original.

        Returns:
            JSON con datos del recurso reactivado y servicios relacionados.
        """
        try:
            data = json.loads(request.body)
            project_resource_id = data.get("id")

            if not project_resource_id:
                return JsonResponse(
                    {"error": "El campo 'id' es requerido."}, status=400
                )

            new_start_date = None
            raw_date = data.get("new_start_date")
            if raw_date:
                try:
                    new_start_date = date.fromisoformat(raw_date)
                except ValueError:
                    return JsonResponse(
                        {"error": "Formato de fecha inválido. Use YYYY-MM-DD."},
                        status=400,
                    )

            result = EquipmentManager.reactivate_in_project(
                project_resource_id, new_start_date=new_start_date
            )

            project_resource = result["project_resource"]

            return JsonResponse(
                {
                    "message": result["message"],
                    "data": self._serialize(project_resource),
                    "related_services_reactivated": result[
                        "related_services_reactivated"
                    ],
                    "related_services_count": len(
                        result["related_services_reactivated"]
                    ),
                },
                status=200,
            )

        except EquipmentManagerError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse(
                {"error": f"Error al reactivar el recurso: {str(e)}"}, status=500
            )

    def _serialize(self, project_resource):
        """Serializa un ProjectResourceItem a dict JSON-serializable."""

        def fmt(d):
            return d.isoformat() if d else None

        return {
            "id": project_resource.id,
            "project_id": project_resource.project.id,
            "type_resource": project_resource.type_resource,
            "resource_item_id": project_resource.resource_item.id,
            "resource_item_code": project_resource.resource_item.code,
            "resource_item_name": project_resource.resource_item.name,
            "detailed_description": project_resource.detailed_description,
            "physical_equipment_code": project_resource.physical_equipment_code,
            "cost": str(project_resource.cost),
            "is_active": project_resource.is_active,
            "is_retired": project_resource.is_retired,
            "operation_start_date": fmt(project_resource.operation_start_date),
            "operation_end_date": fmt(project_resource.operation_end_date),
            "retirement_date": fmt(project_resource.retirement_date),
            "retirement_reason": project_resource.retirement_reason,
        }
