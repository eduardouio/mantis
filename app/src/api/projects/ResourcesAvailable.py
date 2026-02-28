from django.http import JsonResponse
from django.views import View
from django.db.models import Q
from equipment.models import ResourceItem
from projects.models import Project


class ResourcesAvailableAPI(View):
    """Listar todos los equipos activos (no servicios).

    Retorna todos los equipos que estén activos (is_active=True)
    excluyendo los de tipo SERVICIO.
    Para los equipos ocupados incluye la información del proyecto asignado.
    """

    def get(self, request):
        """Obtener lista completa de equipos activos (no servicios)."""
        filters = Q(is_active=True) & ~Q(type_equipment='SERVIC')
        resources = ResourceItem.objects.filter(filters).order_by(
            "type_equipment", "code"
        )

        # Recopilar IDs de proyectos para equipos ocupados
        project_ids = set()
        for r in resources:
            if r.stst_current_project_id:
                project_ids.add(r.stst_current_project_id)

        # Cargar proyectos en un solo query
        projects_map = {}
        if project_ids:
            projects = Project.objects.filter(
                id__in=project_ids
            ).select_related('partner')
            projects_map = {p.id: p for p in projects}

        data = [self._serialize(r, projects_map) for r in resources]

        return JsonResponse(
            {"success": True, "data": data},
            status=200
        )

    def _serialize(self, resource, projects_map):
        """Serializar ResourceItem a JSON."""
        display_name = f"{resource.name} - {resource.get_type_equipment_display()}"

        # Determinar si el recurso está disponible
        is_available = resource.stst_status_disponibility == "DISPONIBLE"

        # Info del proyecto asignado (si está ocupado)
        assigned_project = None
        if not is_available and resource.stst_current_project_id:
            project = projects_map.get(resource.stst_current_project_id)
            if project:
                assigned_project = {
                    "id": project.id,
                    "partner_name": project.partner.name,
                    "location": project.location,
                    "url": f"/projects/{project.id}/",
                }

        return {
            "id": resource.id,
            "code": resource.code,
            "name": resource.name,
            "display_name": display_name,
            "type_equipment": resource.type_equipment,
            "type_equipment_display": resource.get_type_equipment_display(),
            "brand": resource.brand,
            "model": resource.model,
            "status_equipment": resource.stst_status_equipment,
            "status_disponibility": resource.stst_status_disponibility,
            "available": is_available,
            "current_location": resource.stst_current_location,
            "capacity_gallons": (
                str(resource.capacity_gallons) if resource.capacity_gallons else None
            ),
            "assigned_project": assigned_project,
            "is_selected": False,
            "is_confirm_delete": False
        }
