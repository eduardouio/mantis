from django.http import JsonResponse
from django.views import View
import json
from datetime import date

from common.EquipmentManager import EquipmentManager, EquipmentManagerError


class ResourceReleaserAPI(View):
    """API para liberar recursos de un proyecto."""

    def put(self, request):
        """Liberar un recurso de un proyecto."""
        try:
            data = json.loads(request.body)
            project_resource_id = data.get("id")

            if not project_resource_id:
                return JsonResponse(
                    {"error": "ID del recurso es requerido."}, status=400
                )

            retirement_reason = data.get("retirement_reason")

            retirement_date = None
            raw_date = data.get("retirement_date")
            if raw_date:
                try:
                    retirement_date = date.fromisoformat(raw_date)
                except ValueError:
                    pass

            result = EquipmentManager.retire_from_project(
                project_resource_id,
                retirement_reason=retirement_reason,
                retirement_date=retirement_date,
            )

            project_resource = result["project_resource"]

            return JsonResponse(
                {
                    "message": result["message"],
                    "data": self._serialize(project_resource),
                    "related_services_released": result["related_services_released"],
                    "related_services_count": len(result["related_services_released"]),
                },
                status=200,
            )

        except EquipmentManagerError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse(
                {"error": f"Error al liberar el recurso: {str(e)}"}, status=500
            )

    def _serialize(self, project_resource):
        """Serializar un recurso de proyecto."""

        def format_date(d):
            if not d:
                return None
            if isinstance(d, str):
                return d
            return d.isoformat()

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
            "operation_start_date": format_date(project_resource.operation_start_date),
            "operation_end_date": format_date(project_resource.operation_end_date),
        }
