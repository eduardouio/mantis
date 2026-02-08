from django.http import JsonResponse
from django.views import View
import json

from projects.models.Project import ProjectResourceItem


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

            project_resource = ProjectResourceItem.get_by_id(project_resource_id)
            if not project_resource:
                return JsonResponse(
                    {"error": "Recurso del proyecto no encontrado."}, status=404
                )

            if not project_resource.is_active:
                return JsonResponse(
                    {"error": "El recurso ya se encuentra liberado (inactivo)."},
                    status=400,
                )

            if project_resource.type_resource == "SERVICIO":

                project_resource.is_active = False
                project_resource.save()

                return JsonResponse(
                    {
                        "message": "Servicio liberado correctamente.",
                        "data": self._serialize(project_resource),
                    },
                    status=200,
                )

            elif project_resource.type_resource == "EQUIPO":

                resource_item = project_resource.resource_item

                resource_item.stst_release_date = None
                resource_item.stst_commitment_date = None
                resource_item.stst_current_project_id = None
                resource_item.stst_current_location = None
                resource_item.stst_status_disponibility = "DISPONIBLE"
                resource_item.save()

                project_resource.is_active = False
                project_resource.save()

                physical_code = project_resource.physical_equipment_code
                if physical_code and physical_code > 0:
                    related_services = ProjectResourceItem.objects.filter(
                        project=project_resource.project,
                        type_resource="SERVICIO",
                        physical_equipment_code=physical_code,
                        is_active=True,
                    )

                    released_services = []
                    for service in related_services:
                        service.is_active = False
                        service.save()
                        released_services.append(service.id)

                    return JsonResponse(
                        {
                            "message": "Equipo liberado correctamente.",
                            "data": self._serialize(project_resource),
                            "related_services_released": released_services,
                            "related_services_count": len(released_services),
                        },
                        status=200,
                    )

                return JsonResponse(
                    {
                        "message": "Equipo liberado correctamente.",
                        "data": self._serialize(project_resource),
                    },
                    status=200,
                )

            else:
                return JsonResponse({"error": "Tipo de recurso no válido."}, status=400)

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
