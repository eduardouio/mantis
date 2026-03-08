from django.http import JsonResponse
from django.views import View
import json

from projects.models.Project import Project, ProjectResourceItem
from equipment.models.ResourceItem import ResourceItem
from common.EquipmentManager import EquipmentManager, EquipmentManagerError


class AddResourceProjectAPI(View):
    """API para agregar recursos a un proyecto."""

    def post(self, request):
        """Agregar uno o varios recursos al proyecto."""
        data = json.loads(request.body)

        project = Project.get_by_id(data[0]["project_id"])
        if not project:
            raise Exception("Proyecto no encontrado.")

        resource_ids = [r["resource_id"] for r in data]
        resource_map = ResourceItem.objects.in_bulk(resource_ids)

        created_resources = []
        serv_resource_item = None
        maintenance_instances = []

        for resource_data in data:
            resource_item = resource_map.get(resource_data["resource_id"])
            if not resource_item:
                raise Exception(
                    f'Recurso con ID {resource_data["resource_id"]} no encontrado.'
                )

            is_maintenance = "maintenance_cost" in resource_data

            physical_equipment_code = resource_data.get("physical_equipment_code", 0)
            frequency_type = resource_data.get("frequency_type", "DAY")
            interval_days = resource_data.get("interval_days")
            weekdays = resource_data.get("weekdays")
            monthdays = resource_data.get("monthdays")
            operation_start_date = resource_data.get("operation_start_date")

            if is_maintenance:
                # ---- Mantenimiento: lógica original (no la maneja EquipmentManager) ----
                resource_cost = resource_data.get("maintenance_cost", 0.00)

                if serv_resource_item is None:
                    serv_resource_item = ResourceItem.get_by_code("PEISOL-SERV00")
                    if not serv_resource_item:
                        raise Exception(
                            "Recurso de servicio para mantenimiento general "
                            "PEISOL-SERV00 no encontrado. Contacte al administrador."
                        )

                detailed_description = ""
                if physical_equipment_code and physical_equipment_code != 0:
                    try:
                        physical_equipment = ResourceItem.objects.get(
                            id=physical_equipment_code
                        )
                        detailed_description = f"MANTENIMIENTO / {physical_equipment.code}"
                    except ResourceItem.DoesNotExist:
                        pass

                if frequency_type == "DAY" and interval_days is None:
                    interval_days = 1
                elif frequency_type != "DAY" and interval_days is None:
                    interval_days = 0

                maintenance_instances.append(
                    ProjectResourceItem(
                        project=project,
                        resource_item=serv_resource_item,
                        type_resource="SERVICIO",
                        detailed_description=detailed_description,
                        physical_equipment_code=physical_equipment_code,
                        cost=resource_cost,
                        frequency_type=frequency_type,
                        interval_days=interval_days,
                        weekdays=weekdays,
                        monthdays=monthdays,
                        operation_start_date=operation_start_date,
                    )
                )
            else:
                # ---- Alquiler / Servicio normal: delegar a EquipmentManager ----
                type_resource = (
                    "SERVICIO" if resource_item.type_equipment == "SERVIC" else "EQUIPO"
                )
                resource_cost = resource_data.get("cost", 0.00)

                try:
                    if type_resource == "EQUIPO":
                        pr = EquipmentManager.assign_to_project(
                            resource_item=resource_item,
                            project=project,
                            cost=resource_cost,
                            physical_equipment_code=physical_equipment_code,
                            frequency_type=frequency_type,
                            interval_days=interval_days,
                            weekdays=weekdays,
                            monthdays=monthdays,
                            operation_start_date=operation_start_date,
                            commitment_date=resource_data.get("commitment_date"),
                        )
                    else:
                        pr = EquipmentManager.assign_service_to_project(
                            resource_item=resource_item,
                            project=project,
                            cost=resource_cost,
                            physical_equipment_code=physical_equipment_code,
                            frequency_type=frequency_type,
                            interval_days=interval_days,
                            weekdays=weekdays,
                            monthdays=monthdays,
                            operation_start_date=operation_start_date,
                        )
                    created_resources.append(pr)
                except EquipmentManagerError as e:
                    return JsonResponse({"error": str(e)}, status=400)

        # Crear registros de mantenimiento en lote
        if maintenance_instances:
            ProjectResourceItem.objects.bulk_create(maintenance_instances)
            maint_created = ProjectResourceItem.objects.filter(
                project=project
            ).order_by("-id")[: len(maintenance_instances)]
            created_resources.extend(maint_created)

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

    def _serialize(self, project_resource):
        """Serializa un recurso de proyecto para el método GET."""
        return {
            "id": project_resource.id,
            "project_id": project_resource.project.id,
            "project_name": str(project_resource.project),
            "resource_code": project_resource.resource_item.code,
            "resource_name": project_resource.resource_item.name,
            "type_resource": project_resource.type_resource,
            "cost": str(project_resource.cost),
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
        }

    @staticmethod
    def _format_date(d):
        if not d:
            return None
        if isinstance(d, str):
            return d
        return d.isoformat()

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
            "operation_start_date": self._format_date(project_resource.operation_start_date),
            "operation_end_date": self._format_date(project_resource.operation_end_date),
            "is_retired": project_resource.is_retired,
            "retirement_date": self._format_date(project_resource.retirement_date),
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
