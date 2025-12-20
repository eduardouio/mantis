from django.http import JsonResponse
from django.views import View
from projects.models.Project import Project, ProjectResourceItem
from projects.models.CustodyChain import ChainCustodyDetail


class ProjectResources(View):	
    """Manejar recursos asociados a proyectos."""

    def get(self, request, project_id):
        """Obtener recursos asociados a un proyecto."""
        project = Project.get_by_id(project_id)

        if not project:
            return JsonResponse(
                {"error": "Proyecto no encontrado."},
                status=404
            )

        project_resources = ProjectResourceItem.objects.filter(
            project=project
        )
        data = [self._serialize(pr) for pr in project_resources]

        return JsonResponse({"data": data})

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
            "frequency_type": project_resource.frequency_type,
            "interval_days": project_resource.interval_days,
            "weekdays": project_resource.weekdays,
            "monthdays": project_resource.monthdays,
            "operation_start_date": project_resource.operation_start_date.isoformat(),
            "is_active": project_resource.is_active,
            "is_selected": False,
            "type_resource": project_resource.type_resource,
            "is_retired": project_resource.is_retired,
            "retirement_date": project_resource.retirement_date.isoformat() if project_resource.retirement_date else None,
            "retirement_reason": project_resource.retirement_reason,
            "is_confirm_delete": False,
            "is_deleteable": self._is_deletable(project_resource),
            "notes": project_resource.notes
        }


    def _is_deletable(self, project_resource):
        """Determinar si un recurso de proyecto es eliminable."""
        exist = ChainCustodyDetail.get_by_resource_id(project_resource.id)
        if not exist:
            return True
        return False