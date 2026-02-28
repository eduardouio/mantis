from django.http import JsonResponse
from django.views import View
from django.utils import timezone
import json

from projects.models.Project import Project, ProjectResourceItem
from projects.models.SheetProject import SheetProject


class CloseProjectAPI(View):
    """
    API para validar y cerrar un proyecto.
    
    GET  /api/projects/<project_id>/close/ → Valida si el proyecto puede cerrarse
    POST /api/projects/<project_id>/close/ → Ejecuta el cierre del proyecto
    """

    def get(self, request, project_id):
        """Valida si el proyecto puede cerrarse y retorna alertas."""
        try:
            project = self._get_project(project_id)
            if isinstance(project, JsonResponse):
                return project

            if project.is_closed:
                return JsonResponse({
                    "success": False,
                    "can_close": False,
                    "message": "El proyecto ya se encuentra cerrado.",
                    "alerts": []
                }, status=400)

            alerts = self._validate_project(project)
            can_close = not any(a["type"] == "error" for a in alerts)

            return JsonResponse({
                "success": True,
                "can_close": can_close,
                "message": "El proyecto puede cerrarse." if can_close else "El proyecto no puede cerrarse. Revise las alertas.",
                "alerts": alerts,
            })

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error al validar el cierre: {str(e)}"},
                status=500,
            )

    def post(self, request, project_id):
        """Ejecuta el cierre del proyecto."""
        try:
            project = self._get_project(project_id)
            if isinstance(project, JsonResponse):
                return project

            if project.is_closed:
                return JsonResponse({
                    "success": False,
                    "message": "El proyecto ya se encuentra cerrado.",
                }, status=400)

            # Validar antes de cerrar
            alerts = self._validate_project(project)
            has_errors = any(a["type"] == "error" for a in alerts)

            if has_errors:
                return JsonResponse({
                    "success": False,
                    "can_close": False,
                    "message": "No se puede cerrar el proyecto. Revise las alertas.",
                    "alerts": alerts,
                }, status=400)

            # Ejecutar el cierre
            today = timezone.now().date()
            released_equipment = []

            # 1. Liberar todos los recursos tipo EQUIPO que no estén retirados
            active_equipment = ProjectResourceItem.objects.filter(
                project=project,
                type_resource="EQUIPO",
                is_retired=False,
                is_deleted=False,
            )

            for equip in active_equipment:
                # Liberar el recurso físico (ResourceItem)
                resource_item = equip.resource_item
                resource_item.stst_release_date = None
                resource_item.stst_commitment_date = None
                resource_item.stst_current_project_id = None
                resource_item.stst_current_location = None
                resource_item.stst_status_disponibility = "DISPONIBLE"
                resource_item.save()

                # Marcar como retirado
                equip.is_retired = True
                equip.retirement_date = today
                equip.retirement_reason = f"Cierre de proyecto #{project.id}"
                equip.save()

                released_equipment.append({
                    "id": equip.id,
                    "code": equip.resource_item.code,
                    "name": equip.resource_item.name,
                })

                # Liberar servicios relacionados al equipo
                equipment_id = equip.resource_item.id
                related_codes = {equipment_id}
                if equip.physical_equipment_code and equip.physical_equipment_code > 0:
                    related_codes.add(equip.physical_equipment_code)

                related_services = ProjectResourceItem.objects.filter(
                    project=project,
                    type_resource="SERVICIO",
                    physical_equipment_code__in=list(related_codes),
                    is_retired=False,
                    is_deleted=False,
                )
                for service in related_services:
                    service.is_retired = True
                    service.retirement_date = today
                    service.retirement_reason = f"Cierre de proyecto #{project.id}"
                    service.save()

            # 2. Liberar servicios independientes que queden activos
            remaining_services = ProjectResourceItem.objects.filter(
                project=project,
                type_resource="SERVICIO",
                is_retired=False,
                is_deleted=False,
            )
            for service in remaining_services:
                service.is_retired = True
                service.retirement_date = today
                service.retirement_reason = f"Cierre de proyecto #{project.id}"
                service.save()

            # 3. Cerrar el proyecto
            project.is_closed = True
            project.end_date = project.end_date or today
            project.save()

            return JsonResponse({
                "success": True,
                "message": "Proyecto cerrado exitosamente.",
                "released_equipment": released_equipment,
                "released_equipment_count": len(released_equipment),
                "alerts": alerts,
            })

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error al cerrar el proyecto: {str(e)}"},
                status=500,
            )

    def _get_project(self, project_id):
        """Obtiene el proyecto o retorna un error JSON."""
        try:
            return Project.objects.select_related("partner").get(
                pk=project_id, is_active=True, is_deleted=False
            )
        except Project.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Proyecto no encontrado."},
                status=404,
            )

    def _validate_project(self, project):
        """
        Valida todas las condiciones para cerrar el proyecto.
        Retorna una lista de alertas con tipo: error, warning, info.
        """
        alerts = []

        # 1. Verificar planillas en ejecución
        sheets_in_progress = SheetProject.objects.filter(
            project=project,
            status="IN_PROGRESS",
            is_active=True,
            is_deleted=False,
        )
        if sheets_in_progress.exists():
            for sheet in sheets_in_progress:
                alerts.append({
                    "type": "error",
                    "message": f"La planilla #{sheet.id} ({sheet.series_code}) está en ejecución. Debe liquidarla o cancelarla antes de cerrar el proyecto.",
                    "link": f"#/work-sheet/form/{sheet.id}",
                    "link_text": f"Ir a planilla {sheet.series_code}",
                })

        # 2. Verificar planillas sin cerrar (liquidadas pero no cerradas)
        sheets_not_closed = SheetProject.objects.filter(
            project=project,
            is_closed=False,
            is_active=True,
            is_deleted=False,
        ).exclude(status="CANCELLED")
        if sheets_not_closed.exists():
            for sheet in sheets_not_closed:
                alerts.append({
                    "type": "warning",
                    "message": f"La planilla #{sheet.id} ({sheet.series_code}) no está cerrada (Estado: {sheet.get_status_display()}).",
                    "link": f"#/work-sheet/form/{sheet.id}",
                    "link_text": f"Ir a planilla {sheet.series_code}",
                })

        # 3. Verificar recursos activos que serán liberados
        active_equipment = ProjectResourceItem.objects.filter(
            project=project,
            type_resource="EQUIPO",
            is_retired=False,
            is_deleted=False,
        )
        if active_equipment.exists():
            equipment_names = [
                f"{e.resource_item.code} - {e.resource_item.name}"
                for e in active_equipment.select_related("resource_item")
            ]
            alerts.append({
                "type": "info",
                "message": f"Se liberarán {active_equipment.count()} equipo(s) al cerrar el proyecto: {', '.join(equipment_names)}.",
            })

        # 4. Verificar servicios activos
        active_services = ProjectResourceItem.objects.filter(
            project=project,
            type_resource="SERVICIO",
            is_retired=False,
            is_deleted=False,
        )
        if active_services.exists():
            alerts.append({
                "type": "info",
                "message": f"Se retirarán {active_services.count()} servicio(s) activo(s) al cerrar el proyecto.",
            })

        # 5. Si no hay alertas, indicar que todo está listo
        if not alerts:
            alerts.append({
                "type": "info",
                "message": "El proyecto está listo para cerrarse. No se encontraron impedimentos.",
            })

        return alerts
