from django.http import JsonResponse
from django.views import View
from projects.models import SheetProject, SheetProjectDetail


class GetAllSheetProjectAPI(View):
    """Listar todas las hojas de trabajo con filtros."""

    def get(self, request, project_id):
        """Obtener listado de hojas de trabajo."""
        try:
            qs = SheetProject.objects.filter(
                is_active=True,
                project_id=project_id
            ).select_related("project", "project__partner")

            qs = qs.order_by("-created_at")

            sheets = []
            for sheet in qs:
                sheet_data = self._serialize_sheet(sheet)
                details = SheetProjectDetail.objects.filter(
                    sheet_project=sheet, is_active=True
                ).select_related("resource_item")
                
                sheet_data["details"] = [
                    self._serialize_detail(d) for d in details
                ]
                
                sheets.append(sheet_data)

            my_status = 200 if len(sheets) > 0 else 404

            return JsonResponse(
                {"success": True, "count": len(sheets), "data": sheets},
                status=my_status
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def _serialize_sheet(self, sheet):
        return {
            "id": sheet.id,
            "project_id": sheet.project_id,
            "project_name": sheet.project.partner.name,
            "project_location": sheet.project.location or "",
            "issue_date": sheet.issue_date.isoformat() if sheet.issue_date else None,
            "period_start": (
                sheet.period_start.isoformat() if sheet.period_start else None
            ),
            "period_end": sheet.period_end.isoformat() if sheet.period_end else None,
            "status": sheet.status,
            "status_display": sheet.get_status_display(),
            "series_code": sheet.series_code,
            "service_type": sheet.service_type,
            "total_gallons": sheet.total_gallons,
            "total_barrels": sheet.total_barrels,
            "total_cubic_meters": sheet.total_cubic_meters,
            "client_po_reference": sheet.client_po_reference,
            "contact_reference": sheet.contact_reference,
            "contact_phone_reference": sheet.contact_phone_reference,
            "final_disposition_reference": sheet.final_disposition_reference,
            "invoice_reference": sheet.invoice_reference,
            "subtotal": float(sheet.subtotal),
            "tax_amount": float(sheet.tax_amount),
            "total": float(sheet.total),
            "created_at": sheet.created_at.isoformat(),
            "updated_at": sheet.updated_at.isoformat(),
        }

    def _serialize_detail(self, detail):
        """Serializar detalle de hoja de trabajo."""
        return {
            "id": detail.id,
            "resource_item_id": detail.resource_item_id,
            "resource_name": detail.resource_item.name,
            "resource_code": detail.resource_item.code,
            "detail": detail.detail,
            "item_unity": detail.item_unity,
            "quantity": float(detail.quantity),
            "unit_price": float(detail.unit_price),
            "total_line": float(detail.total_line),
            "unit_measurement": detail.unit_measurement,
            "total_price": float(detail.total_price),
        }
