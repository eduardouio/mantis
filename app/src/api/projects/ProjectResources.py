from django.http import JsonResponse
from django.views import View
from projects.models.Project import Project, ProjectResourceItem


class ProjectResources(View):	
    """Manejar recursos asociados a proyectos."""

    def get(self, request, project_id):
        """Obtener recursos asociados a un proyecto."""
        try:
            project = Project.objects.get(
                id=project_id, is_deleted=False, is_active=True
            )
            project_resources = ProjectResourceItem.objects.filter(
                project=project
            )

            data = [self._serialize(pr) for pr in project_resources]

            return JsonResponse({"data": data})

        except Project.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Proyecto no encontrado."},
                status=404
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "error": str(e)},
                status=500
            )

    def _serialize(self, project_resource):
        """Serializar ProjectResourceItem a JSON."""
        return {
            "id": project_resource.id,
            "project_id": project_resource.project.id,
            "type": project_resource.resource_item.type_equipment,
            "resource_item_id": project_resource.resource_item.id,
            "resource_item_code": project_resource.resource_item.code,
            "resource_item_name": project_resource.resource_item.name,
            "detailed_description": project_resource.detailed_description,
            "cost": project_resource.cost,
            "interval_days": project_resource.interval_days,
            "operation_start_date": project_resource.operation_start_date.isoformat(),
            "is_active": project_resource.is_active,
            "is_selected": False,
            "is_confirm_delete": False,
        }
