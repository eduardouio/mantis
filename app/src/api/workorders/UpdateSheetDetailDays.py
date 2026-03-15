import json
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.views import View
from django.db import transaction

from projects.models.SheetProject import SheetProject, SheetProjectDetail


class UpdateSheetDetailDaysAPI(View):
    """
    API para actualizar los días de cobro de alquiler (monthdays_apply_cost)
    de un detalle de planilla de tipo EQUIPO.

    PUT /api/workorders/sheets/detail/<detail_id>/days/
    Body: { "monthdays_apply_cost": [1, 2, 3, ...] }

    Recalcula automáticamente quantity y total_line con base en los días seleccionados.
    """

    def put(self, request, detail_id=None):
        try:
            data = json.loads(request.body)
            return self._update_days(detail_id, data)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "JSON inválido"}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    @transaction.atomic
    def _update_days(self, detail_id, data):
        """Actualizar los días de cobro de un detalle de planilla."""
        if not detail_id:
            return JsonResponse(
                {"success": False, "error": "ID del detalle es requerido"},
                status=400,
            )

        try:
            detail = SheetProjectDetail.objects.select_related(
                "sheet_project", "resource_item", "project_resource_item"
            ).get(id=detail_id, is_active=True)
        except SheetProjectDetail.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Detalle de planilla no encontrado"},
                status=404,
            )

        # Validar que la planilla no esté cerrada
        sheet = detail.sheet_project
        if sheet.is_closed:
            return JsonResponse(
                {
                    "success": False,
                    "error": "No se puede modificar una planilla cerrada",
                },
                status=400,
            )

        # Validar que esté en progreso
        if sheet.status != "IN_PROGRESS":
            return JsonResponse(
                {
                    "success": False,
                    "error": f"No se puede modificar una planilla en estado {sheet.get_status_display()}. "
                             "Solo planillas EN EJECUCIÓN son editables.",
                },
                status=400,
            )

        # Obtener los días del mes
        monthdays = data.get("monthdays_apply_cost")
        if monthdays is None:
            return JsonResponse(
                {
                    "success": False,
                    "error": "El campo monthdays_apply_cost es requerido",
                },
                status=400,
            )

        # Validar que sea una lista de enteros entre 1 y 31
        if not isinstance(monthdays, list):
            return JsonResponse(
                {
                    "success": False,
                    "error": "monthdays_apply_cost debe ser una lista de días",
                },
                status=400,
            )

        # Filtrar y validar días
        valid_days = []
        for day in monthdays:
            try:
                d = int(day)
                if 1 <= d <= 31:
                    valid_days.append(d)
            except (ValueError, TypeError):
                continue

        valid_days = sorted(list(set(valid_days)))

        # Actualizar el detalle
        detail.monthdays_apply_cost = valid_days
        detail.quantity = Decimal(str(len(valid_days)))
        detail.total_line = detail.quantity * detail.unit_price
        detail.save()

        # Recalcular totales de la planilla
        self._recalculate_sheet_totals(sheet)

        return JsonResponse(
            {
                "success": True,
                "message": "Días de cobro actualizados exitosamente",
                "data": {
                    "id": detail.id,
                    "monthdays_apply_cost": detail.monthdays_apply_cost,
                    "quantity": float(detail.quantity),
                    "unit_price": float(detail.unit_price),
                    "total_line": float(detail.total_line),
                    "sheet_totals": {
                        "subtotal": float(sheet.subtotal),
                        "tax_amount": float(sheet.tax_amount),
                        "total": float(sheet.total),
                    },
                },
            }
        )

    def _recalculate_sheet_totals(self, sheet):
        """Recalcular subtotal, IVA y total de la planilla."""
        details = SheetProjectDetail.objects.filter(
            sheet_project=sheet, is_active=True
        )

        subtotal = sum(d.total_line for d in details)
        tax_rate = Decimal("0.15")
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        sheet.subtotal = subtotal
        sheet.tax_amount = tax_amount
        sheet.total = total
        sheet.save()
