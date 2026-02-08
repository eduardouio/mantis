from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.SheetProject import SheetProject, SheetProjectDetail
from projects.models.CustodyChain import CustodyChain
from decimal import Decimal
from calendar import monthrange
from common.WorkSheetBuilder import WorkSheetBuilder


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
        ).select_related("resource_item").order_by("id")

        for sheet_detail in sheet_details:
            resource_item = sheet_detail.resource_item
            
            # Construir la lista de días del mes
            days_list = ["" for d in range(1, 32)]
            monthdays = sheet_detail.monthdays or []
            
            for day in monthdays:
                if 1 <= day <= 31:
                    days_list[day - 1] = "1"
            
            equipment_name = self.get_short_equipment_name(resource_item)
            detail_text = sheet_detail.detail or f"ALQUILER DE {resource_item.name} {resource_item.code}"
            
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
                    "type_resource": "EQUIPO",  # Esto puede ajustarse según necesidad
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

        return context
