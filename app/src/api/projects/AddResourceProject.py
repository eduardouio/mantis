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
                raise Exception(f'Recurso con ID {resource_data["resource_id"]} no encontrado.')
            
            type_resource = "SERVICIO" if resource_item.type_equipment == "SERVIC" else "EQUIPO"
            interval_days = 1 if type_resource == "EQUIPO" else resource_data.get("interval_days", 1)
                
            primary_instances.append(ProjectResourceItem(
                project=project,
                resource_item=resource_item,
                type_resource=type_resource,
                detailed_description=resource_data.get("detailed_description", ""),
                cost=resource_data.get("cost", 0.00),
                interval_days=interval_days,
                operation_start_date=resource_data.get("operation_start_date"),
            ))
            
            have_mantenance = resource_data.get("include_maintenance", False)

            if have_mantenance and type_resource == 'EQUIPO':
                if serv_resource_item is None:
                    serv_resource_item = ResourceItem.get_by_code('PEISOL-SERV00')
                    if not serv_resource_item:
                        raise Exception(
                            'Recurso de servicio para mantenimiento general '
                            ' PESIOL-SERV00 no encontrado. Contacte al administrador.'
                        )
                
                maintenance_instances.append(ProjectResourceItem(
                    project=project,
                    resource_item=serv_resource_item,
                    type_resource='SERVICIO',
                    detailed_description=f'MANTENIMIENTO {resource_item.name}',
                    cost=resource_data.get("maintenance_cost", 0.00),
                    interval_days=resource_data.get("interval_days", 1),
                    operation_start_date=resource_data.get("operation_start_date"),
                ))

            if type_resource == 'EQUIPO':
                resource_item.stst_current_project_id = project.id
                resource_item.stst_commitment_date = resource_data.get("commitment_date")
                resource_item.stst_status_disponibility = 'RENTADO'
                equipment_to_update.append(resource_item)

        if primary_instances:
            ProjectResourceItem.objects.bulk_create(primary_instances)
        if maintenance_instances:
            ProjectResourceItem.objects.bulk_create(maintenance_instances)
        if equipment_to_update:
            ResourceItem.objects.bulk_update(
                equipment_to_update,
                ['stst_current_project_id', 'stst_commitment_date', 'stst_status_disponibility']
            )

        return JsonResponse({"success": True}, status=201)

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
