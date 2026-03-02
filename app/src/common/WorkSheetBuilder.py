from projects.models.SheetProject import SheetProject, SheetProjectDetail
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.SheetMaintenance import SheetMaintenance
from projects.models.ShippingGuide import ShippingGuide, ShippingGuideDetail
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
    - Incluir líneas de hojas de mantenimiento (costo técnico y logístico)
    - Incluir líneas de guías de envío (transporte y estiba)
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
        Calcula los días de alquiler de un equipo según su configuración de frecuencia,
        considerando las fechas de entrada (operation_start_date) y salida
        (retirement_date / operation_end_date) del recurso en el proyecto.
        
        Reglas:
        - La fecha efectiva de inicio es el mayor entre period_start y operation_start_date.
        - La fecha efectiva de fin es el menor entre period_end y la fecha de retiro
          (retirement_date si is_retired, sino operation_end_date). Si no hay fecha de
          retiro/fin, se usa period_end (el equipo estuvo todo el período).
        
        Args:
            project_resource: Instancia de ProjectResourceItem
            
        Returns:
            dict: Diccionario con días del mes como keys (1-31) y 1 si aplica, 0 si no
        """
        days_count = {d: 0 for d in range(1, 32)}
        
        if not self.period_start or not self.period_end:
            return days_count
            
        op_start = project_resource.operation_start_date
        
        # Determinar la fecha de salida del equipo:
        # Si fue retirado (is_retired=True) y tiene retirement_date, usar esa fecha.
        # Si no fue retirado pero tiene operation_end_date, usarla.
        # Si no tiene ninguna, el equipo estuvo todo el período.
        resource_end = None
        if project_resource.is_retired and project_resource.retirement_date:
            resource_end = project_resource.retirement_date
        elif project_resource.operation_end_date:
            resource_end = project_resource.operation_end_date
        
        # Determinar rango efectivo dentro del período de la planilla
        effective_start = max(self.period_start, op_start) if op_start else self.period_start
        effective_end = min(self.period_end, resource_end) if resource_end else self.period_end
        
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
    
    def calculate_service_days(self, project_resource):
        """
        Calcula los días de servicio basándose en las cadenas de custodia.
        
        Para los servicios, los días se determinan por las fechas (activity_date)
        de las cadenas de custodia donde aparezca ese servicio.
        
        Args:
            project_resource: Instancia de ProjectResourceItem
            
        Returns:
            list: Lista de días del mes ordenados y sin duplicados donde el servicio estuvo en una cadena de custodia
        """
        days_set = set()
        
        if not self.period_start or not self.period_end:
            return sorted(list(days_set))
            
        # Obtener todos los detalles de cadenas de custodia para este recurso en esta planilla
        chain_details = ChainCustodyDetail.objects.filter(
            custody_chain__sheet_project=self.sheet_project,
            project_resource=project_resource,
            is_active=True
        ).select_related('custody_chain')
        
        for detail in chain_details:
            chain = detail.custody_chain
            if not chain.is_active:
                continue
                
            activity_date = chain.activity_date
            
            # Verificar que la fecha esté en el período
            if activity_date and self.period_start <= activity_date <= self.period_end:
                day_of_month = activity_date.day
                days_set.add(day_of_month)
                    
        return sorted(list(days_set))
    
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
        
        # Obtener todos los recursos activos del proyecto.
        # Incluimos equipos retirados porque podrían haber estado activos
        # durante parte del período de la planilla (se calcula con retirement_date).
        project_resources = ProjectResourceItem.objects.filter(
            project=self.project,
            is_active=True,
        ).select_related("resource_item").order_by("type_resource", "id")
        
        for project_resource in project_resources:
            resource_item = project_resource.resource_item
            
            # Si el equipo fue retirado antes del inicio del período, omitirlo
            if project_resource.is_retired and project_resource.retirement_date:
                if project_resource.retirement_date < self.period_start:
                    continue
            
            # Calcular días según tipo de recurso
            if project_resource.type_resource == "EQUIPO":
                days_dict = self.calculate_rental_days(project_resource)
                # Para equipos, extraer lista de días del diccionario
                monthdays_list = sorted([day for day, count in days_dict.items() if count > 0])
                quantity = sum(days_dict.values())
            else:  # SERVICIO
                # Para servicios, obtener lista de días desde cadenas de custodia
                monthdays_list = self.calculate_service_days(project_resource)
                quantity = len(monthdays_list)
            
            # Obtener o crear detalle
            detail, created = SheetProjectDetail.objects.get_or_create(
                sheet_project=self.sheet_project,
                resource_item=resource_item,
                project_resource_item=project_resource,
                defaults={
                    'item_unity': 'DIAS',
                    'unit_price': project_resource.cost,
                    'quantity': Decimal(str(quantity)),
                    'detail': project_resource.detailed_description or f"ALQUILER DE {resource_item.name} {resource_item.code}",
                    'reference_document': 'ResourceItem',
                    'id_reference_document': project_resource.id,
                }
            )
            
            # Actualizar si ya existía
            if not created:
                detail.quantity = Decimal(str(quantity))
                detail.unit_price = project_resource.cost
                detail.detail = project_resource.detailed_description or f"ALQUILER DE {resource_item.name} {resource_item.code}"
                detail.reference_document = 'ResourceItem'
                detail.id_reference_document = project_resource.id
            
            # Guardar días del mes en el campo monthdays_apply_cost
            if project_resource.type_resource == "SERVICIO":
                # Para servicios, siempre recalcular desde cadenas de custodia
                detail.monthdays_apply_cost = monthdays_list
            else:
                # Para equipos: si ya tiene días configurados manualmente, respetarlos.
                # Solo asignar los días calculados si es un registro nuevo (recién creado)
                # o si no tiene días configurados aún.
                if created or not detail.monthdays_apply_cost:
                    detail.monthdays_apply_cost = monthdays_list
                else:
                    # Ya tiene días manuales, recalcular quantity desde ellos
                    monthdays_list = detail.monthdays_apply_cost
                    quantity = len(monthdays_list)
                    detail.quantity = Decimal(str(quantity))
            
            # Calcular totales de línea
            detail.total_line = detail.quantity * detail.unit_price
            
            detail.save()
            details.append(detail)
            
        return details

    def build_maintenance_details(self):
        """
        Construye los detalles de la planilla para hojas de mantenimiento.

        Cada hoja de mantenimiento puede generar hasta 2 líneas:
        - Línea de mantenimiento (si cost_total > 0)
        - Línea de logística (si cost_logistics > 0)

        Si alguno de los rubros es cero, esa línea no se incluye.

        Returns:
            list: Lista de instancias SheetProjectDetail creadas
        """
        details = []

        # Eliminar detalles previos de mantenimiento para recalcular
        SheetProjectDetail.objects.filter(
            sheet_project=self.sheet_project,
            reference_document='SheetMaintenance'
        ).delete()

        # Obtener hojas de mantenimiento activas asociadas a esta planilla
        maintenance_sheets = SheetMaintenance.objects.filter(
            id_sheet_project=self.sheet_project,
            is_active=True,
        ).exclude(status='VOID')

        for maintenance in maintenance_sheets:
            resource_item = maintenance.resource_item
            if not resource_item:
                continue

            # Fecha del documento para marcar en el calendario
            doc_date = maintenance.start_date
            monthdays = [doc_date.day] if doc_date else []

            # Línea de costo de mantenimiento
            if maintenance.cost_total and maintenance.cost_total > 0:
                detail = SheetProjectDetail.objects.create(
                    sheet_project=self.sheet_project,
                    resource_item=resource_item,
                    project_resource_item=None,
                    reference_document='SheetMaintenance',
                    id_reference_document=maintenance.id,
                    item_unity='UNIDAD',
                    unit_price=maintenance.cost_total,
                    quantity=Decimal('1'),
                    detail=maintenance.sheet_project_maintenance_concept or "SERVICIO TÉCNICO ESPECIALIZADO",
                    monthdays_apply_cost=monthdays,
                    total_line=maintenance.cost_total * Decimal('1'),
                )
                details.append(detail)

            # Línea de costo logístico
            if maintenance.cost_logistics and maintenance.cost_logistics > 0:
                detail = SheetProjectDetail.objects.create(
                    sheet_project=self.sheet_project,
                    resource_item=resource_item,
                    project_resource_item=None,
                    reference_document='SheetMaintenance',
                    id_reference_document=maintenance.id,
                    item_unity='UNIDAD',
                    unit_price=maintenance.cost_logistics,
                    quantity=Decimal('1'),
                    detail=maintenance.sheet_project_logistics_concept or "LOGÍSTICA",
                    monthdays_apply_cost=monthdays,
                    total_line=maintenance.cost_logistics * Decimal('1'),
                )
                details.append(detail)

        return details

    def build_shipping_guide_details(self):
        """
        Construye los detalles de la planilla para guías de envío.

        Cada guía de envío puede generar hasta 2 líneas:
        - Línea de transporte (si cost_transport > 0)
        - Línea de estiba (si cost_stowage > 0)

        Si alguno de los rubros es cero, esa línea no se incluye.
        La fecha del documento es issue_date. El resource_item se toma
        del primer detalle de la guía.

        Returns:
            list: Lista de instancias SheetProjectDetail creadas
        """
        details = []

        # Eliminar detalles previos de guías de envío para recalcular
        SheetProjectDetail.objects.filter(
            sheet_project=self.sheet_project,
            reference_document='ShippingGuide'
        ).delete()

        if not self.period_start or not self.period_end:
            return details

        # Obtener guías de envío activas del proyecto dentro del período
        shipping_guides = ShippingGuide.objects.filter(
            project=self.project,
            is_active=True,
            issue_date__gte=self.period_start,
            issue_date__lte=self.period_end,
        ).exclude(status='VOID')

        for guide in shipping_guides:
            # Obtener el resource_item del primer detalle de la guía
            first_detail = ShippingGuideDetail.objects.filter(
                shipping_guide=guide,
                is_active=True,
                id_resource_item__isnull=False
            ).select_related('id_resource_item').first()

            if not first_detail or not first_detail.id_resource_item:
                continue

            resource_item = first_detail.id_resource_item

            # Fecha del documento para marcar en el calendario
            doc_date = guide.issue_date
            monthdays = [doc_date.day] if doc_date else []

            # Línea de costo de transporte
            if guide.cost_transport and guide.cost_transport > 0:
                detail = SheetProjectDetail.objects.create(
                    sheet_project=self.sheet_project,
                    resource_item=resource_item,
                    project_resource_item=None,
                    reference_document='ShippingGuide',
                    id_reference_document=guide.id,
                    item_unity='UNIDAD',
                    unit_price=guide.cost_transport,
                    quantity=Decimal('1'),
                    detail=guide.sheet_project_logistics_concept or "TRANSPORTE",
                    monthdays_apply_cost=monthdays,
                    total_line=guide.cost_transport * Decimal('1'),
                )
                details.append(detail)

            # Línea de costo de estiba
            if guide.cost_stowage and guide.cost_stowage > 0:
                detail = SheetProjectDetail.objects.create(
                    sheet_project=self.sheet_project,
                    resource_item=resource_item,
                    project_resource_item=None,
                    reference_document='ShippingGuide',
                    id_reference_document=guide.id,
                    item_unity='UNIDAD',
                    unit_price=guide.cost_stowage,
                    quantity=Decimal('1'),
                    detail=guide.sheet_project_stowage_concept or "ESTIBA",
                    monthdays_apply_cost=monthdays,
                    total_line=guide.cost_stowage * Decimal('1'),
                )
                details.append(detail)

        return details

    def calculate_totals(self):
        """
        Calcula y actualiza los totales en la cabecera de la planilla.
        
        Actualiza:
        - subtotal: Suma de todos los totales de línea
        - tax_amount: IVA (15% del subtotal)
        - total: subtotal + tax_amount
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
        
        # Calcular total
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
        maintenance_details = self.build_maintenance_details()
        shipping_details = self.build_shipping_guide_details()
        totals = self.calculate_totals()
        
        return {
            'sheet_project': self.sheet_project,
            'details_count': len(details) + len(maintenance_details) + len(shipping_details),
            'totals': totals,
        }
