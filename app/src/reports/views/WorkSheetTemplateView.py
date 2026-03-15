from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.SheetProject import SheetProject, SheetProjectDetail
from common.WorkSheetBuilder import WorkSheetBuilder
from datetime import timedelta


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

        # Generar lista de fechas del período para soportar rangos que cruzan meses
        period_dates = []
        if period_start and period_end:
            current_date = period_start
            while current_date <= period_end:
                period_dates.append(current_date)
                current_date += timedelta(days=1)

        num_period_days = len(period_dates) if period_dates else 31

        if period_start and period_end:
            days_in_month = num_period_days

            # Determinar nombre del mes (puede cruzar meses)
            start_month = period_start.month
            end_month = period_end.month
            if start_month == end_month:
                month_name = month_names.get(start_month, "")
            else:
                month_name = f"{month_names.get(start_month, '')} - {month_names.get(end_month, '')}"
        else:
            days_in_month = 31
            month_name = ""

        # Generar headers de días basados en las fechas del período
        day_headers = []
        for dt in period_dates:
            day_headers.append({
                'day': dt.day,
                'month': dt.month,
                'is_new_month': len(day_headers) > 0 and dt.month != period_dates[len(day_headers) - 1].month,
            })
        # Rellenar hasta 31 columnas si hay menos días
        while len(day_headers) < 31:
            day_headers.append({'day': '', 'month': 0, 'is_new_month': False})

        # Leer los datos desde SheetProjectDetail (ya actualizados si estaba en IN_PROGRESS)
        items_list = []

        sheet_details = SheetProjectDetail.objects.filter(
            sheet_project=sheet_project,
            is_active=True
        ).select_related("resource_item", "project_resource_item").order_by("id")

        for sheet_detail in sheet_details:
            resource_item = sheet_detail.resource_item

            # Construir la lista de días basada en posiciones del período
            days_list = ["" for _ in range(31)]
            monthdays = sheet_detail.monthdays_apply_cost or []

            if period_dates:
                # Mapear días del período a posiciones en la tabla
                for i, dt in enumerate(period_dates):
                    if i < 31 and dt.day in monthdays:
                        days_list[i] = "1"
            else:
                # Fallback: mapeo directo por día del mes
                for day in monthdays:
                    if 1 <= day <= 31:
                        days_list[day - 1] = "1"

            detail_text = sheet_detail.detail or f"ALQUILER DE {resource_item.name} {resource_item.code}"

            # Determinar tipo de recurso y nombre de equipo desde project_resource_item
            pri = sheet_detail.project_resource_item
            if sheet_detail.reference_document == 'SheetMaintenance':
                type_resource = "MANTENIMIENTO"
                equipment_name = "MANTENIMIENTO"
            elif sheet_detail.reference_document == 'ShippingGuide':
                type_resource = "GUIA_ENVIO"
                equipment_name = "LOGISTICA"
            elif sheet_detail.reference_document == 'CustodyChain':
                type_resource = "LOGISTICA_CUSTODIA"
                equipment_name = "LOGISTICA"
            else:
                type_resource = pri.type_resource if pri else "EQUIPO"
                equipment_name = self.get_short_equipment_name(resource_item)

            items_list.append(
                {
                    "item_number": 0,  # se reasigna después de ordenar
                    "equipment_name": equipment_name,
                    "detail": detail_text,
                    "quantity": int(sheet_detail.quantity),
                    "unit": sheet_detail.item_unity,
                    "days": days_list,
                    "unit_price": sheet_detail.unit_price,
                    "total_cost": sheet_detail.total_line,
                    "type_resource": type_resource,
                    "resource_item_id": resource_item.id if resource_item else None,
                }
            )

        # --- Ordenar items: alquileres → cadenas custodia (mantenimiento) → cadenas custodia (logística) → guías de remisión → hojas de mantenimiento ---
        rentals = [i for i in items_list if i["type_resource"] == "EQUIPO"]
        services = [i for i in items_list if i["type_resource"] not in (
            "EQUIPO", "MANTENIMIENTO", "GUIA_ENVIO", "LOGISTICA_CUSTODIA"
        )]
        logistics = [i for i in items_list if i["type_resource"] == "LOGISTICA_CUSTODIA"]
        shipping = [i for i in items_list if i["type_resource"] == "GUIA_ENVIO"]
        maintenance = [i for i in items_list if i["type_resource"] == "MANTENIMIENTO"]

        items_list = rentals + services + logistics + shipping + maintenance

        # Reasignar números de ítem en el orden final
        for i, item in enumerate(items_list, 1):
            item["item_number"] = i

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
                "day_headers": day_headers,
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
