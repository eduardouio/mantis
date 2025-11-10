from django.http import JsonResponse
from django.views import View
from django.db import transaction

from projects.models import SheetProject


class DeleteSheetOrderAPI(View):
    """Eliminar (lógicamente) hojas de trabajo."""

    def delete(self, request):
        """Eliminar hoja de trabajo."""
        try:
            sheet_id = request.GET.get("id")
            if not sheet_id:
                return JsonResponse(
                    {"success": False, "error": "ID de hoja de trabajo requerido"},
                    status=400,
                )

            return self._delete_sheet(request, sheet_id)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    @transaction.atomic
    def _delete_sheet(self, request, sheet_id):
        """Eliminar hoja de trabajo y sus detalles."""
        try:
            sheet = SheetProject.objects.get(id=sheet_id, is_active=True)
        except SheetProject.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Hoja de trabajo no encontrada"}, status=404
            )

        if sheet.status == "INVOICED":
            return JsonResponse(
                {"success": False, "error": "No se puede eliminar una hoja facturada"},
                status=400,
            )

        sheet.is_active = False
        sheet.updated_by = request.user
        sheet.save()

        return JsonResponse(
            {"success": True, "message": "Hoja de trabajo eliminada exitosamente"}
        )
