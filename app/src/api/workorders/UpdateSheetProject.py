from django.http import JsonResponse
from django.views import View
from django.db import transaction
import json
from decimal import Decimal, InvalidOperation
from datetime import datetime

from projects.models import Project, SheetProject, SheetProjectDetail, ProjectResourceItem
from projects.models.CustodyChain import ChainCustodyDetail
from equipment.models.ResourceItem import ResourceItem


class UpdateSheetProjectAPI(View):
    """Crear y actualizar hojas de trabajo (SheetProject)."""

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

    def put(self, request, sheet_id=None):
        """Actualizar hoja de trabajo existente."""
        try:
            data = json.loads(request.body)
            if not sheet_id:
                sheet_id = data.get("id")
            if not sheet_id:
                return JsonResponse(
                    {"success": False, "error": "ID de hoja de trabajo requerido"},
                    status=400
                )
            return self._update_sheet(request, sheet_id, data)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "JSON inválido"}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    @transaction.atomic
    def _create_sheet(self, request, data):
        """Crear nueva hoja de trabajo."""
        required_fields = ["project_id", "period_start", "period_end", "service_type"]
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
        
        series_code = SheetProject.get_next_series_code()
        sheet = SheetProject(
            project=project,
            period_start=period_start,
            period_end=period_end,
            status="IN_PROGRESS",
            series_code=series_code,
            secuence_year=int(series_code.split("-")[2]),
            secuence_number=int(series_code.split("-")[3]),
            service_type=data.get("service_type"),
            contact_reference=data.get("contact_reference"),
            contact_phone_reference=data.get("contact_phone_reference")
        )

        sheet.save()

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
                    "status": sheet.status
                },
            },
            status=201
        )

    @transaction.atomic
    def _update_sheet(self, request, sheet_id, data):
        """Actualizar hoja de trabajo existente."""
        try:
            sheet = SheetProject.objects.get(id=sheet_id, is_active=True)
        except SheetProject.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Hoja de trabajo no encontrada"},
                status=404
            )

        # Validar que no esté facturada
        if sheet.status == "INVOICED":
            return JsonResponse(
                {
                    "success": False,
                    "error": "No se puede actualizar una hoja de trabajo facturada"
                },
                status=400
            )

        # Actualizar campos permitidos
        if "period_start" in data:
            period_start = self._parse_date(data["period_start"])
            if period_start:
                sheet.period_start = period_start

        if "period_end" in data:
            period_end = self._parse_date(data["period_end"])
            if period_end:
                sheet.period_end = period_end

        # Validar que period_end sea requerido
        if not sheet.period_end:
            return JsonResponse(
                {"success": False, "error": "La fecha de fin del período es requerida"},
                status=400,
            )
        
        # Validar que la fecha desde sea menor que la fecha hasta
        if sheet.period_start >= sheet.period_end:
            return JsonResponse(
                {"success": False, "error": "La fecha de inicio del período debe ser menor que la fecha de fin"},
                status=400,
            )
        
        # Validar que las fechas no excedan la fecha de fin del proyecto (si existe)
        if sheet.project.end_date:
            if sheet.period_start > sheet.project.end_date:
                return JsonResponse(
                    {"success": False, "error": f"La fecha de inicio del período no puede ser posterior a la fecha de fin del proyecto ({sheet.project.end_date.strftime('%d/%m/%Y')})"},
                    status=400,
                )
            if sheet.period_end > sheet.project.end_date:
                return JsonResponse(
                    {"success": False, "error": f"La fecha de fin del período no puede ser posterior a la fecha de fin del proyecto ({sheet.project.end_date.strftime('%d/%m/%Y')})"},
                    status=400,
                )

        if "service_type" in data:
            sheet.service_type = data["service_type"]

        if "contact_reference" in data:
            sheet.contact_reference = data["contact_reference"]

        if "contact_phone_reference" in data:
            sheet.contact_phone_reference = data["contact_phone_reference"]

        if "client_po_reference" in data:
            sheet.client_po_reference = data["client_po_reference"]

        if "final_disposition_reference" in data:
            sheet.final_disposition_reference = data["final_disposition_reference"]

        if "status" in data and data["status"] in ["IN_PROGRESS", "INVOICED", "CANCELLED"]:
            sheet.status = data["status"]

        sheet.save()

        # Procesar detalles si vienen en el payload
        details_result = []
        if "details" in data:
            result = self._process_details(sheet, data.get("details", []))
            if result.get("error"):
                return JsonResponse(
                    {"success": False, "error": result["error"]},
                    status=400
                )
            details_result = result.get("details", [])

        return JsonResponse(
            {
                "success": True,
                "message": "Hoja de trabajo actualizada exitosamente",
                "data": {
                    "id": sheet.id,
                    "series_code": sheet.series_code,
                    "project_id": sheet.project.id,
                    "period_start": sheet.period_start.isoformat() if sheet.period_start else None,
                    "period_end": sheet.period_end.isoformat() if sheet.period_end else None,
                    "status": sheet.status,
                    "service_type": sheet.service_type,
                    "details": details_result,
                },
            },
            status=200
        )

    def _process_details(self, sheet, received_details):
        """Procesar detalles de la planilla: crear nuevos, mantener existentes, eliminar desmarcados."""
        # 1. Obtener detalles existentes en BD para esta planilla
        existing_details = SheetProjectDetail.objects.filter(
            sheet_project=sheet,
            is_active=True
        )
        existing_details_map = {detail.id: detail for detail in existing_details}

        # 2. Separar los detalles recibidos
        received_existing_ids = set()
        new_details_data = []

        for detail_data in received_details:
            detail_id = detail_data.get("detail_id", 0)
            if detail_id and detail_id > 0:
                # Detalle existente, solo registramos su ID
                received_existing_ids.add(detail_id)
            else:
                # Detalle nuevo (detail_id == 0)
                new_details_data.append(detail_data)

        # 3. Determinar detalles a eliminar (están en BD pero no en los recibidos)
        details_to_delete = set(existing_details_map.keys()) - received_existing_ids

        # 4. Verificar que los detalles a eliminar no tengan cadena de custodia
        for detail_id in details_to_delete:
            detail = existing_details_map[detail_id]
            if detail.project_resource_item:
                has_custody = ChainCustodyDetail.objects.filter(
                    is_active=True,
                    custody_chain__sheet_project=sheet,
                    project_resource_id=detail.project_resource_item.id
                ).exists()
                if has_custody:
                    resource_code = detail.resource_item.code if detail.resource_item else detail_id
                    return {
                        "error": f"No se puede eliminar el detalle '{resource_code}' porque tiene cadenas de custodia registradas en esta planilla"
                    }

        # 5. Eliminar detalles desmarcados (soft delete o hard delete según BaseModel)
        for detail_id in details_to_delete:
            detail = existing_details_map[detail_id]
            detail.delete()

        # 6. Crear detalles nuevos (misma lógica que CreateWorkSheetProjectAPI)
        created_details = []
        for detail_data in new_details_data:
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

            type_resource = detail_data.get("type_resource", "")

            # Obtener el ProjectResourceItem
            physical_equipment_code = None
            project_resource = None
            project_resource_id = detail_data.get("project_resource_id")
            try:
                if project_resource_id:
                    project_resource = ProjectResourceItem.objects.filter(
                        id=project_resource_id,
                        is_deleted=False
                    ).first()
                else:
                    project_resource = ProjectResourceItem.objects.filter(
                        project_id=sheet.project.id,
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
                try:
                    physical_equipment = ResourceItem.objects.get(id=physical_equipment_code, is_active=True)
                    equipment = physical_equipment.get_type_equipment_display() or ""
                except ResourceItem.DoesNotExist:
                    equipment = detail_data.get("detailed_description", "")
            else:
                if type_resource == "SERVICIO":
                    equipment = detail_data.get("detailed_description", "")
                else:
                    equipment = resource_item.get_type_equipment_display() or ""

            item_unity = "DIAS" if type_resource == "SERVICIO" else "UNIDAD"

            detail = SheetProjectDetail(
                sheet_project=sheet,
                resource_item=resource_item,
                project_resource_item=project_resource,
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

        # 7. Construir respuesta con todos los detalles vigentes
        all_details = []
        # Detalles que se mantuvieron
        for detail_id in received_existing_ids:
            if detail_id in existing_details_map:
                detail = existing_details_map[detail_id]
                all_details.append({
                    "id": detail.id,
                    "resource_item_id": detail.resource_item.id,
                    "resource_item_code": detail.resource_item.code,
                    "equipment": detail.equipment,
                    "detail": detail.detail,
                    "item_unity": detail.item_unity,
                    "unit_price": str(detail.unit_price),
                })
        # Detalles nuevos creados
        all_details.extend(created_details)

        return {
            "details": all_details,
            "created": len(created_details),
            "deleted": len(details_to_delete),
            "kept": len(received_existing_ids),
        }

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
