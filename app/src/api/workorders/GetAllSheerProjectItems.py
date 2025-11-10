from projects.models.SheetProject import SheetProject
from django.http import JsonResponse
from django.views import View


class GetAllSheerProjectItemsAPI(View):
    """Retorna información de las hojas de proyecto."""

    def get(self, request, sheet_project_id=None):
        """Obtener información de una hoja de proyecto específica o todas."""
        try:
            if sheet_project_id:
                return self._get_sheet_project_info(sheet_project_id)
            else:
                return self._get_all_sheets_info()
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def _get_sheet_project_info(self, sheet_project_id):
        """Obtener información de una hoja de proyecto específica."""
        try:
            sheet_project = SheetProject.objects.get(
                id=sheet_project_id, is_active=True
            )
        except SheetProject.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Hoja de proyecto no encontrada"},
                status=404,
            )

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "sheet_id": sheet_project.id,
                    "project_id": sheet_project.project.id,
                    "issue_date": sheet_project.issue_date.isoformat()
                    if sheet_project.issue_date
                    else None,
                    "period_start": sheet_project.period_start.isoformat()
                    if sheet_project.period_start
                    else None,
                    "period_end": sheet_project.period_end.isoformat()
                    if sheet_project.period_end
                    else None,
                    "status": sheet_project.status,
                    "series_code": sheet_project.series_code,
                    "service_type": sheet_project.service_type,
                    "subtotal": float(sheet_project.subtotal),
                    "tax_amount": float(sheet_project.tax_amount),
                    "total": float(sheet_project.total),
                    "items": [],  # No hay detalles disponibles
                },
            }
        )

    def _get_all_sheets_info(self):
        """Obtener información de todas las hojas de proyecto activas."""
        sheets = SheetProject.objects.filter(is_active=True).select_related(
            "project__partner"
        )

        all_data = []
        for sheet in sheets:
            all_data.append(
                {
                    "sheet_id": sheet.id,
                    "project_id": sheet.project.id,
                    "issue_date": sheet.issue_date.isoformat()
                    if sheet.issue_date
                    else None,
                    "period_start": sheet.period_start.isoformat()
                    if sheet.period_start
                    else None,
                    "period_end": sheet.period_end.isoformat()
                    if sheet.period_end
                    else None,
                    "status": sheet.status,
                    "series_code": sheet.series_code,
                    "service_type": sheet.service_type,
                    "subtotal": float(sheet.subtotal),
                    "tax_amount": float(sheet.tax_amount),
                    "total": float(sheet.total),
                    "items": [],  # No hay detalles disponibles
                }
            )

        return JsonResponse({"success": True, "data": all_data})
