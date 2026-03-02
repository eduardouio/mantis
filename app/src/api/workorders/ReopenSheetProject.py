from django.http import JsonResponse
from django.views import View
from django.db import transaction
import json

from projects.models.SheetProject import SheetProject


class ReopenSheetProjectAPI(View):
    """Reabrir una planilla que fue liquidada, devolviéndola a estado EN EJECUCIÓN."""

    def put(self, request):
        try:
            data = json.loads(request.body)
            return self._reopen_sheet(data)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "JSON inválido"}, status=400
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "error": str(e)}, status=500
            )

    @transaction.atomic
    def _reopen_sheet(self, data):
        sheet_id = data.get("id")
        if not sheet_id:
            return JsonResponse(
                {"success": False, "error": "Se requiere el ID de la planilla"},
                status=400,
            )

        try:
            sheet = SheetProject.objects.get(id=sheet_id, is_active=True)
        except SheetProject.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Planilla no encontrada"},
                status=404,
            )

        # Solo se puede reabrir si está LIQUIDATED
        if sheet.status != "LIQUIDATED":
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Solo se puede reabrir una planilla liquidada. "
                             f"Estado actual: {sheet.get_status_display()}",
                },
                status=400,
            )

        # No se puede reabrir si está cerrada
        if sheet.is_closed:
            return JsonResponse(
                {
                    "success": False,
                    "error": "No se puede reabrir una planilla cerrada",
                },
                status=400,
            )

        sheet.status = "IN_PROGRESS"
        sheet.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Planilla reabierta exitosamente",
                "data": {
                    "id": sheet.id,
                    "series_code": sheet.series_code,
                    "status": sheet.status,
                },
            },
            status=200,
        )
