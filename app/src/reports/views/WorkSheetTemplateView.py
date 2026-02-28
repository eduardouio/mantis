from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.SheetProject import SheetProject, SheetProjectDetail
from calendar import monthrange
from common.WorkSheetBuilder import WorkSheetBuilder
from datetime import date


EQUIPMENT_SHORT_NAMES = {
    "SERVIC": "SERVICIO",
    "LVMNOS": "LAVAMANOS",
    "BTSNHM": "BATERIAS",
    "BTSNMJ": "BATERIAS",
    "EST4UR": "URINARIOS",
    "CMPRBN": "CAMPER",
    "PTRTAP": "PTAP",
    "PTRTAR": "PTAR",
    "TNQAAC": "TANQUE",
    "TNQAAR": "TANQUE",
}


class WorkSheetTemplateView(TemplateView):
    template_name = "reports/worksheet_template.html"

    def get_short_equipment_name(self, resource_item):
        """Obtiene el nombre corto del tipo de equipo."""
        type_code = getattr(resource_item, "type_equipment", None)
        if type_code and type_code in EQUIPMENT_SHORT_NAMES:
            return EQUIPMENT_SHORT_NAMES[type_code]
        return resource_item.name if hasattr(resource_item, "name") else "EQUIPO"

    def _days_to_ranges(self, days_list):
        """Convierte una lista de días [1,2,3,5,6,10] en rangos '1-3, 5-6, 10'."""
        if not days_list:
            return ""
        sorted_days = sorted(set(days_list))
        ranges = []
        start = sorted_days[0]
        end = sorted_days[0]
        for d in sorted_days[1:]:
            if d == end + 1:
                end = d
            else:
                ranges.append(f"{start}-{end}" if start != end else str(start))
                start = d
                end = d
        ranges.append(f"{start}-{end}" if start != end else str(start))
        return ", ".join(ranges)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sheet_id = kwargs.get("id")
        sheet_project = get_object_or_404(SheetProject, id=sheet_id)

        # Si la planilla está en progreso, actualizar datos con WorkSheetBuilder
        if sheet_project.status == "IN_PROGRESS":
            builder = WorkSheetBuilder(sheet_project)
            builder.build()
            # Recargar el objeto para obtener los totales actualizados
            sheet_project.refresh_from_db()

        project = sheet_project.project
        partner = project.partner if project else None

        period_start = sheet_project.period_start
        period_end = sheet_project.period_end

        validation_errors = []

        if not period_start or not period_end:
            validation_errors.append(
                "La planilla no tiene fechas de período definidas. "
                "Por favor configure las fechas de inicio y fin del período."
            )

        if period_start and period_end:
            year = period_start.year
            month = period_start.month
            days_in_month = monthrange(year, month)[1]
        else:
            days_in_month = 31
            month = 1
            year = 2026

        month_names = {
            1: "ENERO",
            2: "FEBRERO",
            3: "MARZO",
            4: "ABRIL",
            5: "MAYO",
            6: "JUNIO",
            7: "JULIO",
            8: "AGOSTO",
            9: "SEPTIEMBRE",
            10: "OCTUBRE",
            11: "NOVIEMBRE",
            12: "DICIEMBRE",
        }
        month_name = month_names.get(month, "")

        # Leer los datos desde SheetProjectDetail (ya actualizados si estaba en IN_PROGRESS)
        items_list = []
        item_number = 0

        sheet_details = SheetProjectDetail.objects.filter(
            sheet_project=sheet_project,
            is_active=True
        ).select_related("resource_item", "project_resource_item").order_by("id")

        for sheet_detail in sheet_details:
            resource_item = sheet_detail.resource_item
            
            # Construir la lista de días del mes
            days_list = ["" for d in range(1, 32)]
            monthdays = sheet_detail.monthdays_apply_cost or []
            
            for day in monthdays:
                if 1 <= day <= 31:
                    days_list[day - 1] = "1"
            
            equipment_name = self.get_short_equipment_name(resource_item)
            detail_text = sheet_detail.detail or f"ALQUILER DE {resource_item.name} {resource_item.code}"
            
            # Determinar tipo de recurso desde project_resource_item
            pri = sheet_detail.project_resource_item
            type_resource = pri.type_resource if pri else "EQUIPO"
            
            # Para equipos, calcular fechas efectivas y rangos de días
            effective_start = None
            effective_end = None
            days_range_text = ""
            
            if type_resource == "EQUIPO" and pri and period_start and period_end:
                # Fecha efectiva de inicio
                op_start = pri.operation_start_date
                effective_start = max(period_start, op_start) if op_start else period_start
                
                # Fecha efectiva de fin
                if pri.is_retired and pri.retirement_date:
                    resource_end = pri.retirement_date
                elif pri.operation_end_date:
                    resource_end = pri.operation_end_date
                else:
                    resource_end = period_end
                effective_end = min(period_end, resource_end)
                
                # Convertir los días seleccionados en texto de rangos
                days_range_text = self._days_to_ranges(monthdays)
            
            item_number += 1
            
            items_list.append(
                {
                    "item_number": item_number,
                    "equipment_name": equipment_name,
                    "detail": detail_text,
                    "quantity": int(sheet_detail.quantity),
                    "unit": sheet_detail.item_unity,
                    "days": days_list,
                    "unit_price": sheet_detail.unit_price,
                    "total_cost": sheet_detail.total_line,
                    "type_resource": type_resource,
                    "effective_start": effective_start,
                    "effective_end": effective_end,
                    "days_range_text": days_range_text,
                }
            )

        # Usar los totales ya calculados en la cabecera
        subtotal = sheet_project.subtotal
        tax_amount = sheet_project.tax_amount
        total = sheet_project.total
        total_gallons = sheet_project.total_gallons
        total_barrels = sheet_project.total_barrels
        total_cubic_meters = sheet_project.total_cubic_meters

        context.update(
            {
                "sheet_project": sheet_project,
                "project": project,
                "partner": partner,
                "period_start": period_start,
                "period_end": period_end,
                "month_name": month_name,
                "days_in_month": days_in_month,
                "days_range": range(1, days_in_month + 1),
                "all_days_range": range(1, 32),
                "items": items_list,
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "total": total,
                "total_gallons": total_gallons,
                "total_barrels": total_barrels,
                "total_cubic_meters": total_cubic_meters,
                "validation_errors": validation_errors,
            }
        )

        # Datos de firma del usuario
        if self.request.user.is_authenticated:
            context['siganture_name'] = self.request.user.siganture_name or ''
            context['siganture_role'] = self.request.user.siganture_role or ''

        return context
