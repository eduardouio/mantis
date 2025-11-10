from django.http import JsonResponse
from django.views import View
from django.db import transaction
import json
from datetime import datetime

from projects.models import Project, SheetProject, SheetProjectDetail
from equipment.models import ResourceItem


class AddUpdateSheetProjectAPI(View):
    """Crear o actualizar hojas de trabajo (SheetProject)."""

    def post(self, request):
        """Crear nueva hoja de trabajo."""
        try:
            data = json.loads(request.body)
            return self._create_sheet(request, data)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "JSON inválido"}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def put(self, request):
        """Actualizar hoja de trabajo existente."""
        try:
            data = json.loads(request.body)
            return self._update_sheet(request, data)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "JSON inválido"}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def get(self, request):
        """Obtener una hoja de trabajo por ID o el siguiente código de serie."""
        try:

            if request.GET.get("next_series"):
                next_code = SheetProject.generate_next_series_code()
                return JsonResponse({"success": True, "series_code": next_code})

            sheet_id = request.GET.get("id")
            if not sheet_id:
                return JsonResponse(
                    {"success": False, "error": "ID de hoja de trabajo requerido"},
                    status=400,
                )

            sheet = (
                SheetProject.objects.filter(id=sheet_id, is_active=True)
                .select_related("project", "project__partner")
                .first()
            )

            if not sheet:
                return JsonResponse(
                    {"success": False, "error": "Hoja de trabajo no encontrada"},
                    status=404,
                )

            details = SheetProjectDetail.objects.filter(
                sheet_project=sheet, is_active=True
            ).select_related("resource_item")

            return JsonResponse(
                {
                    "success": True,
                    "data": {
                        "sheet": self._serialize_sheet(sheet),
                        "details": [self._serialize_detail(d) for d in details],
                    },
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    @transaction.atomic
    def _create_sheet(self, request, data):
        """Crear nueva hoja de trabajo con detalles."""

        required_fields = ["project_id"]
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            return JsonResponse(
                {
                    "success": False,
                    "error": f'Campos requeridos: {", ".join(missing_fields)}',
                },
                status=400,
            )

        try:
            project = Project.objects.get(id=data["project_id"], is_active=True)
        except Project.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Proyecto no encontrado"}, status=404
            )

        existing = SheetProject.objects.filter(
            project=project, status="IN_PROGRESS", is_active=True
        ).exists()

        if existing:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Ya existe una hoja de trabajo en progreso para este proyecto",
                },
                status=400,
            )

        issue_date = self._parse_date(data.get("issue_date"))
        period_start = self._parse_date(data.get("period_start"))
        period_end = self._parse_date(data.get("period_end"))

        sheet = SheetProject.objects.create(
            project=project,
            issue_date=issue_date,
            period_start=period_start,
            period_end=period_end,
            status=data.get("status", "IN_PROGRESS"),
            series_code=data.get("series_code", "PSL-PS-00000-00"),
            service_type=data.get("service_type", "ALQUILER DE EQUIPOS"),
            total_gallons=data.get("total_gallons", 0),
            total_barrels=data.get("total_barrels", 0),
            total_cubic_meters=data.get("total_cubic_meters", 0),
            client_po_reference=data.get("client_po_reference"),
            contact_reference=data.get("contact_reference"),
            contact_phone_reference=data.get("contact_phone_reference"),
            final_disposition_reference=data.get("final_disposition_reference"),
            invoice_reference=data.get("invoice_reference"),
            subtotal=data.get("subtotal", 0),
            tax_amount=data.get("tax_amount", 0),
            total=data.get("total", 0),
            created_by=request.user,
            updated_by=request.user,
        )

        details_data = data.get("details", [])
        created_details = []
        for detail_data in details_data:
            detail = self._add_detail(sheet, detail_data, request.user)
            if detail:
                created_details.append(detail)

        return JsonResponse(
            {
                "success": True,
                "message": "Hoja de trabajo creada exitosamente",
                "data": {
                    "sheet": self._serialize_sheet(sheet),
                    "details": [self._serialize_detail(d) for d in created_details],
                },
            }
        )

    @transaction.atomic
    def _update_sheet(self, request, data):
        """Actualizar hoja de trabajo existente."""
        sheet_id = data.get("id")
        if not sheet_id:
            return JsonResponse(
                {"success": False, "error": "ID de hoja de trabajo requerido"},
                status=400,
            )

        try:
            sheet = SheetProject.objects.get(id=sheet_id, is_active=True)
        except SheetProject.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Hoja de trabajo no encontrada"}, status=404
            )

        if sheet.status == "INVOICED":
            return JsonResponse(
                {
                    "success": False,
                    "error": "No se puede editar una hoja de trabajo facturada",
                },
                status=400,
            )

        if "issue_date" in data:
            sheet.issue_date = self._parse_date(data["issue_date"])
        if "period_start" in data:
            sheet.period_start = self._parse_date(data["period_start"])
        if "period_end" in data:
            sheet.period_end = self._parse_date(data["period_end"])
        if "status" in data:
            sheet.status = data["status"]
        if "series_code" in data:
            sheet.series_code = data["series_code"]
        if "service_type" in data:
            sheet.service_type = data["service_type"]
        if "total_gallons" in data:
            sheet.total_gallons = data["total_gallons"]
        if "total_barrels" in data:
            sheet.total_barrels = data["total_barrels"]
        if "total_cubic_meters" in data:
            sheet.total_cubic_meters = data["total_cubic_meters"]
        if "client_po_reference" in data:
            sheet.client_po_reference = data["client_po_reference"]
        if "contact_reference" in data:
            sheet.contact_reference = data["contact_reference"]
        if "contact_phone_reference" in data:
            sheet.contact_phone_reference = data["contact_phone_reference"]
        if "final_disposition_reference" in data:
            sheet.final_disposition_reference = data["final_disposition_reference"]
        if "invoice_reference" in data:
            sheet.invoice_reference = data["invoice_reference"]
        if "subtotal" in data:
            sheet.subtotal = data["subtotal"]
        if "tax_amount" in data:
            sheet.tax_amount = data["tax_amount"]
        if "total" in data:
            sheet.total = data["total"]

        sheet.updated_by = request.user
        sheet.save()

        if "details" in data:

            SheetProjectDetail.objects.filter(sheet_project=sheet).update(
                is_active=False
            )

            created_details = []
            for detail_data in data["details"]:
                detail = self._add_detail(sheet, detail_data, request.user)
                if detail:
                    created_details.append(detail)

            details = created_details
        else:
            details = SheetProjectDetail.objects.filter(
                sheet_project=sheet, is_active=True
            ).select_related("resource_item")

        return JsonResponse(
            {
                "success": True,
                "message": "Hoja de trabajo actualizada exitosamente",
                "data": {
                    "sheet": self._serialize_sheet(sheet),
                    "details": [self._serialize_detail(d) for d in details],
                },
            }
        )

    def _add_detail(self, sheet, detail_data, user):
        """Agregar detalle a la hoja de trabajo."""
        resource_id = detail_data.get("resource_item_id")
        if not resource_id:
            return None

        try:
            resource = ResourceItem.objects.get(id=resource_id, is_active=True)
        except ResourceItem.DoesNotExist:
            return None

        detail = SheetProjectDetail.objects.create(
            sheet_project=sheet,
            resource_item=resource,
            detail=detail_data.get("detail", ""),
            item_unity=detail_data.get("item_unity", "DIAS"),
            quantity=detail_data.get("quantity", 0),
            unit_price=detail_data.get("unit_price", 0),
            total_line=detail_data.get("total_line", 0),
            unit_measurement=detail_data.get("unit_measurement", "DAIS"),
            total_price=detail_data.get("total_price", 0),
            created_by=user,
            updated_by=user,
        )
        return detail

    def _parse_date(self, date_str):
        """Parsear fecha desde string."""
        if not date_str:
            return None
        if isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None
        return date_str

    def _serialize_sheet(self, sheet):
        """Serializar hoja de trabajo."""
        return {
            "id": sheet.id,
            "project_id": sheet.project_id,
            "project_name": f'{sheet.project.partner.name} - {sheet.project.location or ""}',
            "issue_date": sheet.issue_date.isoformat() if sheet.issue_date else None,
            "period_start": (
                sheet.period_start.isoformat() if sheet.period_start else None
            ),
            "period_end": sheet.period_end.isoformat() if sheet.period_end else None,
            "status": sheet.status,
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
