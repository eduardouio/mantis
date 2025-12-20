from django.http import JsonResponse
from django.views import View
import json

from projects.models.Project import Project, ProjectResourceItem
from equipment.models.ResourceItem import ResourceItem


class AddResourceProjectAPI(View):
    """API para agregar recursos a un proyecto."""

    def post(self, request):
        """Agregar uno o varios recursos al proyecto."""
        data = json.loads(request.body)

        # ipdb.set_trace()
        project = Project.get_by_id(data[0]["project_id"])
        if not project:
            raise Exception("Proyecto no encontrado.")

        resource_ids = [r["resource_id"] for r in data]
        resource_map = ResourceItem.objects.in_bulk(resource_ids)

        primary_instances = []
        maintenance_instances = []
        equipment_to_update = []
        serv_resource_item = None

        for resource_data in data:
            resource_item = resource_map.get(resource_data["resource_id"])
            if not resource_item:
                raise Exception(
                    f'Recurso con ID {resource_data["resource_id"]} no encontrado.'
                )

            type_resource = (
                "SERVICIO" if resource_item.type_equipment == "SERVIC" else "EQUIPO"
            )
            
            # Extraer configuración de frecuencia del payload
            p_freq_type = resource_data.get("frequency_type", "DAY")
            p_interval = resource_data.get("interval_days", 1)
            p_weekdays = resource_data.get("weekdays")
            p_monthdays = resource_data.get("monthdays")

            if type_resource == "SERVICIO":
                resource_cost = resource_data.get("maintenance_cost", 0.00)
                # Si es servicio, usa la configuración de frecuencia del payload
                prim_freq_type = p_freq_type
                prim_interval = p_interval
                prim_weekdays = p_weekdays
                prim_monthdays = p_monthdays
            else:
                resource_cost = resource_data.get("cost", 0.00)
                # Si es equipo (renta), configuración por defecto (diaria)
                prim_freq_type = "DAY"
                prim_interval = 1
                prim_weekdays = None
                prim_monthdays = None

            primary_instances.append(
                ProjectResourceItem(
                    project=project,
                    resource_item=resource_item,
                    type_resource=type_resource,
                    detailed_description=resource_data.get("detailed_description", ""),
                    cost=resource_cost,
                    frequency_type=prim_freq_type,
                    interval_days=prim_interval,
                    weekdays=prim_weekdays,
                    monthdays=prim_monthdays,
                    operation_start_date=resource_data.get("operation_start_date"),
                )
            )

            have_mantenance = resource_data.get("include_maintenance", False)

            if have_mantenance and type_resource == "EQUIPO":
                if serv_resource_item is None:
                    serv_resource_item = ResourceItem.get_by_code("PEISOL-SERV00")
                    if not serv_resource_item:
                        raise Exception(
                            "Recurso de servicio para mantenimiento general "
                            " PESIOL-SERV00 no encontrado. Contacte al administrador."
                        )

                maintenance_cost = resource_data.get("maintenance_cost", 0.00)

                maintenance_instances.append(
                    ProjectResourceItem(
                        project=project,
                        resource_item=serv_resource_item,
                        type_resource="SERVICIO",
                        detailed_description=f"MANTENIMIENTO {resource_item.name}",
                        cost=maintenance_cost,
                        frequency_type=p_freq_type,
                        interval_days=p_interval,
                        weekdays=p_weekdays,
                        monthdays=p_monthdays,
                        operation_start_date=resource_data.get("operation_start_date"),
                    )
                )

            if type_resource == "EQUIPO":
                resource_item.stst_current_project_id = project.id
                resource_item.stst_commitment_date = resource_data.get(
                    "commitment_date"
                )
                resource_item.stst_status_disponibility = "RENTADO"
                resource_item.stst_current_location = project.location
                equipment_to_update.append(resource_item)

        created_resources = []

        if primary_instances:
            ProjectResourceItem.objects.bulk_create(primary_instances)
            created_primary_ids = ProjectResourceItem.objects.filter(
                project=project,
                resource_item_id__in=resource_ids,
                type_resource__in=["EQUIPO", "SERVICIO"],
            ).order_by("-id")[: len(primary_instances)]
            created_resources.extend(created_primary_ids)

        if maintenance_instances:
            ProjectResourceItem.objects.bulk_create(maintenance_instances)
            created_maintenance_ids = ProjectResourceItem.objects.filter(
                project=project,
                resource_item=serv_resource_item,
                type_resource="SERVICIO",
            ).order_by("-id")[: len(maintenance_instances)]
            created_resources.extend(created_maintenance_ids)

        if equipment_to_update:
            ResourceItem.objects.bulk_update(
                equipment_to_update,
                [
                    "stst_current_project_id",
                    "stst_commitment_date",
                    "stst_status_disponibility",
                    "stst_current_location",
                ],
            )

        serialized_data = [
            self._serialize_project_resource(resource) for resource in created_resources
        ]

        return JsonResponse({"data": serialized_data}, status=201)

    def get(self, request):
        """Listar recursos de un proyecto."""
        try:
            project_id = request.GET.get("project_id")
            resource_id = request.GET.get("resource_id")

            if project_id:
                qs = ProjectResourceItem.objects.filter(
                    project_id=project_id, is_active=True, is_retired=False
                ).select_related("project", "resource_item")
                data = [self._serialize(r) for r in qs]
                return JsonResponse({"success": True, "data": data})

            if resource_id:
                qs = ProjectResourceItem.objects.filter(
                    resource_item_id=resource_id, is_active=True, is_retired=False
                ).select_related("project", "resource_item")
                data = [self._serialize(r) for r in qs]

                return JsonResponse({"success": True, "data": data})

            return JsonResponse(
                {
                    "success": False,
                    "error": "Debe proporcionar project_id o resource_id",
                },
                status=400,
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def _serialize_project_resource(self, project_resource):
        return {
            "id": project_resource.id,
            "project_id": project_resource.project.id,
            "project_name": str(project_resource.project),
            "resource_item_id": project_resource.resource_item.id,
            "resource_item_name": project_resource.resource_item.name,
            "type_resource": project_resource.type_resource,
            "detailed_description": project_resource.detailed_description,
            "cost": float(project_resource.cost),
            "interval_days": project_resource.interval_days,
            "operation_start_date": (
                project_resource.operation_start_date.isoformat()
                if project_resource.operation_start_date
                else None
            ),
            "operation_end_date": (
                project_resource.operation_end_date.isoformat()
                if project_resource.operation_end_date
                else None
            ),
            "is_retired": project_resource.is_retired,
            "retirement_date": (
                project_resource.retirement_date.isoformat()
                if project_resource.retirement_date
                else None
            ),
            "retirement_reason": project_resource.retirement_reason,
            "is_active": project_resource.is_active,
            "is_deleted": project_resource.is_deleted,
            "created_at": (
                project_resource.created_at.isoformat()
                if hasattr(project_resource, "created_at")
                and project_resource.created_at
                else None
            ),
            "updated_at": (
                project_resource.updated_at.isoformat()
                if hasattr(project_resource, "updated_at")
                and project_resource.updated_at
                else None
            ),
        }
