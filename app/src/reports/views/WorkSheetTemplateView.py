from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.SheetProject import SheetProject, SheetProjectDetail
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.Project import ProjectResourceItem
from decimal import Decimal
from calendar import monthrange
from datetime import date, timedelta



EQUIPMENT_SHORT_NAMES = {
    'SERVIC': 'SERVICIO',
    'LVMNOS': 'LAVAMANOS',
    'BTSNHM': 'BATERIAS',
    'BTSNMJ': 'BATERIAS',
    'EST4UR': 'URINARIOS',
    'CMPRBN': 'CAMPER',
    'PTRTAP': 'PTAP',
    'PTRTAR': 'PTAR',
    'TNQAAC': 'TANQUE',
    'TNQAAR': 'TANQUE',
}


class WorkSheetTemplateView(TemplateView):
    template_name = "reports/worksheet_template.html"

    def get_short_equipment_name(self, resource_item):
        """Obtiene el nombre corto del tipo de equipo."""
        type_code = getattr(resource_item, 'type_equipment', None)
        if type_code and type_code in EQUIPMENT_SHORT_NAMES:
            return EQUIPMENT_SHORT_NAMES[type_code]
        return resource_item.name if hasattr(resource_item, 'name') else 'EQUIPO'

    def calculate_rental_days(self, project_resource, period_start, period_end, days_in_month):
        """
        Calcula los días de alquiler de un equipo según su configuración de frecuencia.
        Retorna un diccionario con los días del mes marcados.
        """
        days_count = {d: 0 for d in range(1, 32)}
        
        
        op_start = project_resource.operation_start_date
        op_end = project_resource.operation_end_date
        
        
        effective_start = max(period_start, op_start) if op_start else period_start
        effective_end = min(period_end, op_end) if op_end else period_end
        
        if effective_start > effective_end:
            return days_count
        
        frequency_type = project_resource.frequency_type
        
        current_date = effective_start
        while current_date <= effective_end:
            day_of_month = current_date.day
            
            if frequency_type == 'DAY':
                
                days_count[day_of_month] = 1
                
            elif frequency_type == 'WEEK':
                
                weekdays = project_resource.weekdays or []
                if current_date.weekday() in weekdays:
                    days_count[day_of_month] = 1
                    
            elif frequency_type == 'MONTH':
                
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
        
        
        if period_start and period_end:
            year = period_start.year
            month = period_start.month
            days_in_month = monthrange(year, month)[1]
        else:
            days_in_month = 31
            month = 1
            year = 2026
        
        
        month_names = {
            1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL',
            5: 'MAYO', 6: 'JUNIO', 7: 'JULIO', 8: 'AGOSTO',
            9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
        }
        month_name = month_names.get(month, '')
        
        items_list = []
        subtotal = Decimal('0')
        item_number = 0
        
        
        
        
        equipment_resources = ProjectResourceItem.objects.filter(
            project=project,
            type_resource='EQUIPO',
            is_active=True,
            is_retired=False
        ).select_related('resource_item')
        
        for project_resource in equipment_resources:
            resource_item = project_resource.resource_item
            
            
            sheet_detail = SheetProjectDetail.objects.filter(
                sheet_project=sheet_project,
                resource_item=resource_item
            ).first()
            
            unit_price = sheet_detail.unit_price if sheet_detail else project_resource.cost
            item_unity = sheet_detail.item_unity if sheet_detail else 'DIAS'
            
            
            days_count = self.calculate_rental_days(
                project_resource, period_start, period_end, days_in_month
            )
            
            
            total_days = sum(1 for d in range(1, days_in_month + 1) if days_count[d] > 0)
            
            if total_days > 0:
                item_number += 1
                unit_price_decimal = Decimal(str(unit_price)) if unit_price else Decimal('0')
                total_cost = total_days * unit_price_decimal
                subtotal += total_cost
                
                
                days_list = ['1' if days_count[d] > 0 else '' for d in range(1, 32)]
                
                
                equipment_name = self.get_short_equipment_name(resource_item)
                detail = project_resource.detailed_description or f"ALQUILER DE {resource_item.name} {resource_item.code}"
                
                items_list.append({
                    'item_number': item_number,
                    'equipment_name': equipment_name,
                    'detail': detail,
                    'quantity': total_days,
                    'unit': item_unity,
                    'days': days_list,
                    'unit_price': unit_price_decimal,
                    'total_cost': total_cost,
                    'type_resource': 'EQUIPO',
                })
        
        
        
        
        
        custody_chains = CustodyChain.objects.filter(
            sheet_project=sheet_project,
            is_active=True
        ).select_related('technical', 'vehicle')
        
        
        service_days_count = {d: 0 for d in range(1, 32)}
        service_total_cost = Decimal('0')
        service_detail_parts = []
        
        for chain in custody_chains:
            chain_details = ChainCustodyDetail.objects.filter(
                custody_chain=chain,
                is_active=True
            ).select_related(
                'project_resource__resource_item',
                'project_resource__project'
            )
            
            activity_day = chain.activity_date.day if chain.activity_date else None
            
            for detail in chain_details:
                project_resource = detail.project_resource
                
                
                if project_resource.type_resource != 'SERVICIO':
                    continue
                
                
                if activity_day and 1 <= activity_day <= 31:
                    service_days_count[activity_day] = 1
                
                
                resource_item = project_resource.resource_item
                sheet_detail = SheetProjectDetail.objects.filter(
                    sheet_project=sheet_project,
                    resource_item=resource_item
                ).first()
                
                unit_price = sheet_detail.unit_price if sheet_detail else project_resource.cost
                unit_price_decimal = Decimal(str(unit_price)) if unit_price else Decimal('0')
                service_total_cost += unit_price_decimal
                
                
                detail_text = project_resource.detailed_description or f"{resource_item.name}"
                if detail_text not in service_detail_parts:
                    service_detail_parts.append(detail_text)
        
        
        total_service_days = sum(1 for d in range(1, days_in_month + 1) if service_days_count[d] > 0)
        
        if total_service_days > 0 or service_total_cost > 0:
            item_number += 1
            subtotal += service_total_cost
            
            days_list = ['1' if service_days_count[d] > 0 else '' for d in range(1, 32)]
            
            
            if total_service_days > 0:
                unit_price_service = service_total_cost / total_service_days
            else:
                unit_price_service = service_total_cost
            
            items_list.append({
                'item_number': item_number,
                'equipment_name': 'SERVICIO',
                'detail': 'MANTENIMIENTO DE EQUIPOS' if not service_detail_parts else ', '.join(service_detail_parts[:2]),
                'quantity': total_service_days,
                'unit': 'DIAS',
                'days': days_list,
                'unit_price': unit_price_service,
                'total_cost': service_total_cost,
                'type_resource': 'SERVICIO',
            })
        
        
        tax_rate = Decimal('0.15')
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        
        total_gallons = sum(chain.total_gallons or 0 for chain in custody_chains)
        total_barrels = sum(chain.total_barrels or 0 for chain in custody_chains)
        total_cubic_meters = sum(chain.total_cubic_meters or 0 for chain in custody_chains)
        total_cubic_meters = sum(chain.total_cubic_meters or 0 for chain in custody_chains)
        
        context.update({
            'sheet_project': sheet_project,
            'project': project,
            'partner': partner,
            'period_start': period_start,
            'period_end': period_end,
            'month_name': month_name,
            'days_in_month': days_in_month,
            'days_range': range(1, days_in_month + 1),
            'all_days_range': range(1, 32),
            'items': items_list,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total': total,
            'total_gallons': total_gallons,
            'total_barrels': total_barrels,
            'total_cubic_meters': total_cubic_meters,
        })
        
        return context