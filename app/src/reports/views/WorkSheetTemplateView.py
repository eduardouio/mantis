from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.SheetProject import SheetProject, SheetProjectDetail
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.Project import ProjectResourceItem
from decimal import Decimal
from calendar import monthrange
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

    def calculate_rental_days(
        self, project_resource, period_start, period_end, days_in_month
    ):
        """
        Calcula los días de alquiler de un equipo según su configuración de frecuencia.
        Retorna un diccionario con los días del mes marcados.
        """
        days_count = {d: 0 for d in range(1, 32)}

        op_start = project_resource.operation_start_date
        op_end = project_resource.operation_end_date

        if not period_start or not period_end:
            return days_count

        effective_start = max(period_start, op_start) if op_start else period_start
        effective_end = min(period_end, op_end) if op_end else period_end

        if effective_start > effective_end:
            return days_count

        frequency_type = project_resource.frequency_type

        current_date = effective_start
        while current_date <= effective_end:
            day_of_month = current_date.day

            if frequency_type == "DAY":

                days_count[day_of_month] = 1

            elif frequency_type == "WEEK":

                weekdays = project_resource.weekdays or []
                if current_date.weekday() in weekdays:
                    days_count[day_of_month] = 1

            elif frequency_type == "MONTH":

                monthdays = project_resource.monthdays or []
                if day_of_month in monthdays:
                    days_count[day_of_month] = 1

            current_date += timedelta(days=1)

        return days_count

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sheet_id = kwargs.get("id")
        sheet_project = get_object_or_404(SheetProject, id=sheet_id)

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

        items_list = []
        subtotal = Decimal("0")
        item_number = 0

        # Obtener todos los recursos del proyecto (equipos y servicios)
        project_resources = ProjectResourceItem.objects.filter(
            project=project,
            is_active=True,
            is_retired=False
        ).select_related("resource_item").order_by("type_resource", "id")

        # Crear un ítem por cada recurso
        for project_resource in project_resources:
            resource_item = project_resource.resource_item
            
            # Obtener precio del detalle de la planilla o del costo del recurso
            sheet_detail = SheetProjectDetail.objects.filter(
                sheet_project=sheet_project, 
                resource_item=resource_item
            ).first()

            unit_price = sheet_detail.unit_price if sheet_detail else project_resource.cost
            item_unity = sheet_detail.item_unity if sheet_detail else "DIAS"
            
            unit_price_decimal = Decimal(str(unit_price)) if unit_price else Decimal("0")
            
            # Determinar los días según el tipo de recurso
            days_list = ["" for d in range(1, 32)]
            quantity = 0
            
            if project_resource.type_resource == "EQUIPO":
                # Para equipos: usar calculate_rental_days
                if period_start and period_end:
                    days_dict = self.calculate_rental_days(
                        project_resource, period_start, period_end, days_in_month
                    )
                    for day in range(1, 32):
                        if days_dict.get(day, 0) == 1:
                            days_list[day - 1] = "1"
                    quantity = sum(1 for v in days_dict.values() if v == 1)
            
            elif project_resource.type_resource == "SERVICIO":
                # Para servicios: obtener días de las cadenas de custodia
                chain_details = ChainCustodyDetail.objects.filter(
                    custody_chain__sheet_project=sheet_project,
                    custody_chain__is_active=True,
                    project_resource=project_resource,
                    is_active=True
                ).select_related("custody_chain")
                
                # Marcar los días según activity_date de cada cadena
                for detail in chain_details:
                    activity_date = detail.custody_chain.activity_date
                    if activity_date and period_start and period_end:
                        if period_start <= activity_date <= period_end:
                            day_of_month = activity_date.day
                            if 1 <= day_of_month <= 31:
                                days_list[day_of_month - 1] = "1"
                
                quantity = sum(1 for d in days_list if d == "1")
            
            # Calcular costo total
            total_cost = unit_price_decimal * Decimal(str(quantity))
            subtotal += total_cost
            
            equipment_name = self.get_short_equipment_name(resource_item)
            detail_text = (
                project_resource.detailed_description
                or f"ALQUILER DE {resource_item.name} {resource_item.code}"
            )
            
            item_number += 1
            
            items_list.append(
                {
                    "item_number": item_number,
                    "equipment_name": equipment_name,
                    "detail": detail_text,
                    "quantity": quantity,
                    "unit": item_unity,
                    "days": days_list,
                    "unit_price": unit_price_decimal,
                    "total_cost": total_cost,
                    "type_resource": project_resource.type_resource,
                }
            )

        custody_chains = CustodyChain.objects.filter(
            sheet_project=sheet_project, is_active=True
        ).select_related("technical", "vehicle")

        tax_rate = Decimal("0.15")
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        total_gallons = sum(chain.total_gallons or 0 for chain in custody_chains)
        total_barrels = sum(chain.total_barrels or 0 for chain in custody_chains)
        total_cubic_meters = sum(
            chain.total_cubic_meters or 0 for chain in custody_chains
        )

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
