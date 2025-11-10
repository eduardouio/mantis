from projects.models.SheetProject import SheetProject, SheetProjectDetail
from equipment.models.Vehicle import Vehicle
from accounts.models.Technical import Technical
from django.http import JsonResponse
from django.views import View


class GetAllSheerProjectItemsAPI(View):
    """Retorna todos los items relacionados a las hojas de proyecto."""

    def get(self, request, sheet_project_id=None):
        """Obtener items de una hoja de proyecto específica o todas."""
        try:
            if sheet_project_id:
                return self._get_sheet_project_items(sheet_project_id)
            else:
                return self._get_all_items()
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def _get_sheet_project_items(self, sheet_project_id):
        """Obtener items de una hoja de proyecto específica."""
        try:
            sheet_project = SheetProject.objects.get(
                id=sheet_project_id, is_active=True
            )
        except SheetProject.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Hoja de proyecto no encontrada"},
                status=404,
            )

        details = SheetProjectDetail.objects.filter(
            sheet_project=sheet_project, is_active=True
        ).select_related("resource_item")

        items = []
        for detail in details:
            item_data = {
                "detail_id": detail.id,
                "resource_item": self._get_resource_item_data(detail.resource_item),
                "issue_date": (
                    detail.issue_date.isoformat() if detail.issue_date else None
                ),
                "detail": detail.detail,
                "item_unity": detail.item_unity,
                "quantity": float(detail.quantity),
                "unit_price": float(detail.unit_price),
                "total_line": float(detail.total_line),
                "unit_measurement": detail.unit_measurement,
                "total_price": float(detail.total_price),
            }

            if detail.id_technical:
                item_data["technical"] = self._get_technical_data(detail.id_technical)

            if detail.id_vehicle:
                item_data["vehicle"] = self._get_vehicle_data(detail.id_vehicle)

            items.append(item_data)

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "project_id": sheet_project.project.id,
                    "items": items,
                },
            }
        )

    def _get_all_items(self):
        """Obtener todos los items de todas las hojas de proyecto activas."""
        sheets = SheetProject.objects.filter(is_active=True).select_related(
            "project__partner"
        )

        all_data = []
        for sheet in sheets:
            details = SheetProjectDetail.objects.filter(
                sheet_project=sheet, is_active=True
            ).select_related("resource_item")

            items = []
            for detail in details:
                item_data = {
                    "detail_id": detail.id,
                    "resource_item": self._get_resource_item_data(detail.resource_item),
                    "issue_date": (
                        detail.issue_date.isoformat() if detail.issue_date else None
                    ),
                    "detail": detail.detail,
                    "item_unity": detail.item_unity,
                    "quantity": float(detail.quantity),
                    "unit_price": float(detail.unit_price),
                    "total_line": float(detail.total_line),
                }

                if detail.id_technical:
                    item_data["technical"] = self._get_technical_data(
                        detail.id_technical
                    )

                if detail.id_vehicle:
                    item_data["vehicle"] = self._get_vehicle_data(detail.id_vehicle)

                items.append(item_data)

            all_data.append(
                {
                    "project_id": sheet.project.id,
                    "items": items,
                }
            )

        return JsonResponse({"success": True, "data": all_data})

    def _get_resource_item_data(self, resource_item):
        """Obtener datos del recurso."""
        return {
            "id": resource_item.id,
            "name": resource_item.name,
            "code": resource_item.code,
            "type_equipment": resource_item.type_equipment,
            "brand": resource_item.brand,
            "model": resource_item.model,
            "status": resource_item.stst_status_equipment,
            "availability": resource_item.stst_status_disponibility,
        }

    def _get_technical_data(self, technical_id):
        """Obtener datos del técnico."""
        try:
            technical = Technical.objects.get(id=technical_id, is_active=True)
            return {
                "id": technical.id,
                "name": f"{technical.first_name} {technical.last_name}",
            }
        except Technical.DoesNotExist:
            return None

    def _get_vehicle_data(self, vehicle_id):
        """Obtener datos del vehículo."""
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id, is_active=True)
            return {
                "id": vehicle.id,
                "no_plate": vehicle.no_plate,
                "type_vehicle": vehicle.type_vehicle,
                "brand": vehicle.brand,
                "model": vehicle.model,
            }
        except Vehicle.DoesNotExist:
            return None
