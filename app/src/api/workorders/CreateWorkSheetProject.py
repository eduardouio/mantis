from django.http import JsonResponse
from django.views import View
from django.db import transaction
import json
from decimal import Decimal, InvalidOperation
from datetime import datetime

from projects.models import Project, SheetProject, SheetProjectDetail, ProjectResourceItem
from equipment.models.ResourceItem import ResourceItem


class CreateWorkSheetProjectAPI(View):
    """Crear hojas de trabajo (SheetProject)."""

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

    @transaction.atomic
    def _create_sheet(self, request, data):
        """Crear nueva hoja de trabajo."""
        required_fields = ["project_id", "period_start", "period_end"]
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

        period_start = self._parse_date(data.get("period_start"))
        period_end = self._parse_date(data.get("period_end"))

        if not period_start:
            return JsonResponse(
                {"success": False, "error": "Fecha de inicio de período inválida"},
                status=400,
            )

        if not period_end:
            return JsonResponse(
                {"success": False, "error": "Fecha de fin de período inválida"},
                status=400,
            )

        # Validar que la fecha desde sea menor que la fecha hasta
        if period_start >= period_end:
            return JsonResponse(
                {"success": False, "error": "La fecha de inicio del período debe ser menor que la fecha de fin"},
                status=400,
            )

        # Validar que las fechas no excedan la fecha de fin del proyecto (si existe)
        if project.end_date:
            if period_start > project.end_date:
                return JsonResponse(
                    {"success": False, "error": f"La fecha de inicio del período no puede ser posterior a la fecha de fin del proyecto ({project.end_date.strftime('%d/%m/%Y')})"},
                    status=400,
                )
            if period_end > project.end_date:
                return JsonResponse(
                    {"success": False, "error": f"La fecha de fin del período no puede ser posterior a la fecha de fin del proyecto ({project.end_date.strftime('%d/%m/%Y')})"},
                    status=400,
                )

        # Generar series_code y extraer componentes
        series_code = SheetProject.get_next_series_code()
        parts = series_code.split("-")
        secuence_prefix = f"{parts[0]}-{parts[1]}"
        secuence_year = int(parts[2])
        secuence_number = int(parts[3])

        # Determinar status: usar el del JSON o por defecto IN_PROGRESS
        status = data.get("status", "IN_PROGRESS")
        if status not in ("IN_PROGRESS", "INVOICED", "CANCELLED"):
            status = "IN_PROGRESS"

        issue_date = self._parse_date(data.get("issue_date"))

        sheet = SheetProject(
            project=project,
            issue_date=issue_date,
            period_start=period_start,
            period_end=period_end,
            status=status,
            series_code=series_code,
            secuence_prefix=secuence_prefix,
            secuence_year=secuence_year,
            secuence_number=secuence_number,
            service_type=data.get("service_type", "ALQUILER Y MANTENIMIENTO"),
            client_po_reference=data.get("client_po_reference"),
            contact_reference=data.get("contact_reference"),
            contact_phone_reference=data.get("contact_phone_reference"),
            final_disposition_reference=data.get("final_disposition_reference"),
            invoice_reference=data.get("invoice_reference"),
        )

        sheet.save()

        # Procesar los detalles (recursos seleccionados)
        details = data.get("details", [])
        created_details = []

        for detail_data in details:
            resource_item_id = detail_data.get("resource_item_id")
            if not resource_item_id:
                continue

            try:
                resource_item = ResourceItem.objects.get(id=resource_item_id, is_active=True)
            except ResourceItem.DoesNotExist:
                continue

            # unit_price desde cost
            try:
                unit_price = Decimal(str(detail_data.get("cost", 0)))
            except (InvalidOperation, TypeError, ValueError):
                unit_price = Decimal("0")

            # item_unity: SERVICIO -> DIAS, EQUIPO -> UNIDAD
            type_resource = detail_data.get("type_resource", "")
            
            # Buscar el ProjectResourceItem para obtener el physical_equipment_code
            physical_equipment_code = None
            try:
                project_resource = ProjectResourceItem.objects.filter(
                    project_id=project.id,
                    resource_item_id=resource_item_id,
                    type_resource=type_resource,
                    is_deleted=False
                ).first()
                if project_resource:
                    physical_equipment_code = project_resource.physical_equipment_code
            except Exception:
                pass
            
            # Obtener descripción legible del tipo de equipo
            equipment = ""
            if physical_equipment_code and physical_equipment_code != 0:
                # Si tiene equipo físico asociado, obtener su tipo legible
                try:
                    physical_equipment = ResourceItem.objects.get(id=physical_equipment_code, is_active=True)
                    equipment = physical_equipment.get_type_equipment_display() or ""
                except ResourceItem.DoesNotExist:
                    equipment = detail_data.get("detailed_description", "")
            else:
                # Si no tiene equipo físico, usar descripción o tipo del recurso actual
                if type_resource == "SERVICIO":
                    equipment = detail_data.get("detailed_description", "")
                else:
                    equipment = resource_item.get_type_equipment_display() or ""
            item_unity = "DIAS" if type_resource == "SERVICIO" else "UNIDAD"

            detail = SheetProjectDetail(
                sheet_project=sheet,
                resource_item=resource_item,
                equipment=equipment,
                detail=detail_data.get("detailed_description", ""),
                item_unity=item_unity,
                quantity=Decimal("0"),
                unit_price=unit_price,
                total_line=Decimal("0"),
                monthdays_apply_cost=None,
            )
            detail.save()
            created_details.append({
                "id": detail.id,
                "resource_item_id": resource_item.id,
                "resource_item_code": resource_item.code,
                "equipment": detail.equipment,
                "detail": detail.detail,
                "item_unity": detail.item_unity,
                "unit_price": str(detail.unit_price),
            })

        return JsonResponse(
            {
                "success": True,
                "message": "Hoja de trabajo creada exitosamente",
                "data": {
                    "id": sheet.id,
                    "series_code": sheet.series_code,
                    "project_id": project.id,
                    "period_start": sheet.period_start.isoformat(),
                    "period_end": sheet.period_end.isoformat() if sheet.period_end else None,
                    "status": sheet.status,
                    "service_type": sheet.service_type,
                    "client_po_reference": sheet.client_po_reference,
                    "invoice_reference": sheet.invoice_reference,
                    "contact_reference": sheet.contact_reference,
                    "contact_phone_reference": sheet.contact_phone_reference,
                    "final_disposition_reference": sheet.final_disposition_reference,
                    "details_count": len(created_details),
                    "details": created_details,
                },
            },
            status=201,
        )

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
