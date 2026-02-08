from projects.models.SheetProject import SheetProject, SheetProjectDetail
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.Project import ProjectResourceItem
from decimal import Decimal
from datetime import timedelta
from calendar import monthrange


class WorkSheetBuilder:
    """
    Constructor de planillas de proyecto.
    
    Se encarga de:
    - Calcular días de alquiler de equipos según frecuencia configurada
    - Calcular días de servicio basándose en cadenas de custodia
    - Crear/actualizar detalles de la planilla (SheetProjectDetail)
    - Actualizar totales en la cabecera (SheetProject)
    """
    
    def __init__(self, sheet_project):
        """
        Inicializa el constructor con una planilla de proyecto.
        
        Args:
            sheet_project: Instancia de SheetProject
        """
        self.sheet_project = sheet_project
        self.project = sheet_project.project
        self.period_start = sheet_project.period_start
        self.period_end = sheet_project.period_end
        
    def calculate_rental_days(self, project_resource):
        """
        Calcula los días de alquiler de un equipo según su configuración de frecuencia.
        
        Args:
            project_resource: Instancia de ProjectResourceItem
            
        Returns:
            dict: Diccionario con días del mes como keys (1-31) y 1 si aplica, 0 si no
        """
        days_count = {d: 0 for d in range(1, 32)}
        
        if not self.period_start or not self.period_end:
            return days_count
            
        op_start = project_resource.operation_start_date
        op_end = project_resource.operation_end_date
        
        # Determinar rango efectivo
        effective_start = max(self.period_start, op_start) if op_start else self.period_start
        effective_end = min(self.period_end, op_end) if op_end else self.period_end
        
        if effective_start > effective_end:
            return days_count
            
        frequency_type = project_resource.frequency_type
        
        current_date = effective_start
        while current_date <= effective_end:
            day_of_month = current_date.day
            
            if frequency_type == "DAY":
                # Todos los días en el rango
                days_count[day_of_month] = 1
                
            elif frequency_type == "WEEK":
                # Días específicos de la semana
                weekdays = project_resource.weekdays or []
                if current_date.weekday() in weekdays:
                    days_count[day_of_month] = 1
                    
            elif frequency_type == "MONTH":
                # Días específicos del mes
                monthdays = project_resource.monthdays or []
                if day_of_month in monthdays:
                    days_count[day_of_month] = 1
                    
            current_date += timedelta(days=1)
            
        return days_count
    
    def calculate_service_days(self, resource_item):
        """
        Calcula los días de servicio basándose en las cadenas de custodia.
        
        Args:
            resource_item: Instancia de ResourceItem
            
        Returns:
            dict: Diccionario con días del mes como keys (1-31) y 1 si aplica, 0 si no
        """
        days_count = {d: 0 for d in range(1, 32)}
        
        if not self.period_start or not self.period_end:
            return days_count
            
        # Obtener cadenas de custodia del período
        custody_chains = CustodyChain.objects.filter(
            sheet_project=self.sheet_project,
            is_active=True
        )
        
        for chain in custody_chains:
            # Obtener detalles de la cadena que contengan este recurso
            chain_details = ChainCustodyDetail.objects.filter(
                custody_chain=chain,
                resource_item=resource_item,
                is_active=True
            )
            
            for detail in chain_details:
                service_date = detail.service_date
                
                # Verificar que la fecha esté en el período
                if service_date and self.period_start <= service_date <= self.period_end:
                    day_of_month = service_date.day
                    days_count[day_of_month] = 1
                    
        return days_count
    
    def build_details(self):
        """
        Construye o actualiza todos los detalles de la planilla (SheetProjectDetail).
        
        Procesa cada recurso del proyecto:
        - Equipos: calcula días según frecuencia configurada
        - Servicios: calcula días según cadenas de custodia
        
        Returns:
            list: Lista de instancias SheetProjectDetail creadas/actualizadas
        """
        details = []
        
        # Obtener todos los recursos activos del proyecto
        project_resources = ProjectResourceItem.objects.filter(
            project=self.project,
            is_active=True,
            is_retired=False
        ).select_related("resource_item").order_by("type_resource", "id")
        
        for project_resource in project_resources:
            resource_item = project_resource.resource_item
            
            # Calcular días según tipo de recurso
            if project_resource.type_resource == "EQUIPO":
                days_dict = self.calculate_rental_days(project_resource)
            else:  # SERVICIO
                days_dict = self.calculate_service_days(resource_item)
            
            # Calcular cantidad total de días
            quantity = sum(days_dict.values())
            
            # Obtener o crear detalle
            detail, created = SheetProjectDetail.objects.get_or_create(
                sheet_project=self.sheet_project,
                resource_item=resource_item,
                defaults={
                    'item_unity': 'DIAS',
                    'unit_price': project_resource.cost,
                    'quantity': Decimal(str(quantity)),
                    'detail': project_resource.detailed_description or f"ALQUILER DE {resource_item.name} {resource_item.code}",
                }
            )
            
            # Actualizar si ya existía
            if not created:
                detail.quantity = Decimal(str(quantity))
                detail.unit_price = project_resource.cost
                detail.detail = project_resource.detailed_description or f"ALQUILER DE {resource_item.name} {resource_item.code}"
            
            # Guardar días del mes en el campo monthdays
            detail.monthdays = [day for day, count in days_dict.items() if count > 0]
            
            # Calcular totales de línea
            detail.total_line = detail.quantity * detail.unit_price
            detail.total_price = detail.total_line
            
            detail.save()
            details.append(detail)
            
        return details
    
    def calculate_totals(self):
        """
        Calcula y actualiza los totales en la cabecera de la planilla.
        
        Actualiza:
        - subtotal: Suma de todos los totales de línea
        - tax_amount: IVA (15%)
        - total: Subtotal + IVA
        - total_gallons, total_barrels, total_cubic_meters: De las cadenas de custodia
        """
        # Calcular subtotal desde los detalles
        details = SheetProjectDetail.objects.filter(
            sheet_project=self.sheet_project,
            is_active=True
        )
        
        subtotal = sum(detail.total_line for detail in details)
        
        # Calcular IVA (15%)
        tax_rate = Decimal("0.15")
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        # Calcular totales de volúmenes desde cadenas de custodia
        custody_chains = CustodyChain.objects.filter(
            sheet_project=self.sheet_project,
            is_active=True
        )
        
        total_gallons = sum(chain.total_gallons or 0 for chain in custody_chains)
        total_barrels = sum(chain.total_barrels or 0 for chain in custody_chains)
        total_cubic_meters = sum(chain.total_cubic_meters or 0 for chain in custody_chains)
        
        # Actualizar cabecera
        self.sheet_project.subtotal = subtotal
        self.sheet_project.tax_amount = tax_amount
        self.sheet_project.total = total
        self.sheet_project.total_gallons = total_gallons
        self.sheet_project.total_barrels = total_barrels
        self.sheet_project.total_cubic_meters = total_cubic_meters
        self.sheet_project.save()
        
        return {
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total': total,
            'total_gallons': total_gallons,
            'total_barrels': total_barrels,
            'total_cubic_meters': total_cubic_meters,
        }
    
    def build(self):
        """
        Construye la planilla completa: detalles y totales.
        
        Este es el método principal que ejecuta todo el proceso:
        1. Construye los detalles de la planilla
        2. Calcula y actualiza los totales
        
        Returns:
            dict: Diccionario con información del resultado
        """
        details = self.build_details()
        totals = self.calculate_totals()
        
        return {
            'sheet_project': self.sheet_project,
            'details_count': len(details),
            'totals': totals,
        }
