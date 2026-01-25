from django.http import JsonResponse
from django.views import View
from django.db import transaction
import json
from datetime import datetime

from projects.models import SheetProject


class UpdateSheetOrderAPI(View):
    """Actualizar hojas de trabajo."""

    def put(self, request):
        """Actualizar hoja de trabajo."""
        try:
            data = json.loads(request.body)
            sheet_id = data.get("id")

            if not sheet_id:
                return JsonResponse(
                    {"success": False, "error": "ID de hoja de trabajo requerido"},
                    status=400,
                )

            return self._update_sheet(request, sheet_id, data)

        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "JSON inválido"}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    @transaction.atomic
    def _update_sheet(self, request, sheet_id, data):
        """Actualizar hoja de trabajo."""
        try:
            sheet = SheetProject.objects.get(id=sheet_id, is_active=True)
        except SheetProject.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Hoja de trabajo no encontrada"}, status=404
            )

        # Validar que no esté facturada
        if sheet.status == "INVOICED":
            return JsonResponse(
                {
                    "success": False,
                    "error": "No se puede modificar una hoja facturada",
                },
                status=400,
            )

        # Actualizar campos permitidos
        if "period_start" in data:
            try:
                sheet.period_start = datetime.strptime(
                    data["period_start"], "%Y-%m-%d"
                ).date()
            except ValueError:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Formato de fecha inválido para period_start",
                    },
                    status=400,
                )

        if "period_end" in data:
            try:
                sheet.period_end = datetime.strptime(
                    data["period_end"], "%Y-%m-%d"
                ).date()
            except ValueError:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Formato de fecha inválido para period_end",
                    },
                    status=400,
                )

        # Validar que period_start sea menor que period_end
        if sheet.period_start and sheet.period_end:
            if sheet.period_start > sheet.period_end:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "La fecha de inicio debe ser menor que la fecha de fin",
                    },
                    status=400,
                )

        if "service_type" in data:
            valid_types = ["ALQUILER", "MANTENIMIENTO", "ALQUILER Y MANTENIMIENTO"]
            if data["service_type"] not in valid_types:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Tipo de servicio inválido. Valores permitidos: {', '.join(valid_types)}",
                    },
                    status=400,
                )
            sheet.service_type = data["service_type"]

        if "contact_reference" in data:
            sheet.contact_reference = data["contact_reference"]

        if "contact_phone_reference" in data:
            sheet.contact_phone_reference = data["contact_phone_reference"]

        if "client_po_reference" in data:
            sheet.client_po_reference = data["client_po_reference"]

        if "final_disposition_reference" in data:
            sheet.final_disposition_reference = data["final_disposition_reference"]

        if "invoice_reference" in data:
            sheet.invoice_reference = data["invoice_reference"]

        # Actualizar metadatos
        sheet.updated_by = request.user
        sheet.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Hoja de trabajo actualizada exitosamente",
                "data": {
                    "id": sheet.id,
                    "period_start": (
                        sheet.period_start.isoformat() if sheet.period_start else None
                    ),
                    "period_end": (
                        sheet.period_end.isoformat() if sheet.period_end else None
                    ),
                    "service_type": sheet.service_type,
                    "contact_reference": sheet.contact_reference,
                    "contact_phone_reference": sheet.contact_phone_reference,
                    "client_po_reference": sheet.client_po_reference,
                    "final_disposition_reference": sheet.final_disposition_reference,
                    "invoice_reference": sheet.invoice_reference,
                    "status": sheet.status,
                    "series_code": sheet.series_code,
                },
            }
        )
