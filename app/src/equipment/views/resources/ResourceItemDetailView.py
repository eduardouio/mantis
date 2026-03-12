from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView

from common.StatusResourceItem import StatusResourceItem
from equipment.models import ResourceItem
from projects.models import ProjectResourceItem, SheetMaintenance


class ResourceItemDetailView(LoginRequiredMixin, DetailView):
    model = ResourceItem
    template_name = 'presentations/resource_presentation.html'
    context_object_name = 'equipment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment = self.object
        today = timezone.now().date()

        # Información básica
        context['title_section'] = f'Ficha de Equipo - {equipment.name}'
        context['title_page'] = f'Ficha de Equipo - {equipment.name}'
        context['today'] = today

        # Obtener el parámetro de acción de la URL
        context['action'] = self.request.GET.get('action', None)

        # Detectar si es un servicio
        is_service = getattr(equipment, 'type_equipment', None) == 'SERVIC'
        context['is_service'] = is_service
        context['resource_type'] = 'servicio' if is_service else 'equipo'

        if is_service:
            # Para servicios: solo información básica y auditoría
            context['equipment_status'] = getattr(equipment, 'stst_status_equipment', 'DESCONOCIDO')
            return context

        # Para equipos: información completa
        project_information = self._get_project_information(equipment)

        # Estadísticas de uso del equipo
        context.update(self._get_equipment_statistics(project_information))

        # Información de proyectos asociados
        context.update(project_information)

        # Información de estado y mantenimiento
        context.update(self._get_maintenance_information(equipment, project_information))

        # Metadatos del sistema
        context.update(self._get_system_metadata(equipment))

        # Características específicas del equipo
        context.update(self._get_equipment_characteristics(equipment))

        # Componentes especiales (blower, motor, banda, etc.)
        context.update(self._get_special_components(equipment))

        # Información detallada de capacidad
        context.update(self._get_capacity_information(equipment))

        # Información de estado del equipo usando StatusResourceItem
        context.update(self._get_equipment_status_analysis(equipment))

        return context

    def _get_equipment_statistics(self, project_information):
        """Calcula estadísticas del equipo basadas en sus asignaciones."""
        project_assignments = project_information['project_assignments']
        equipment_project_timeline = project_information['equipment_project_timeline']
        
        # Calcular totales usando el campo 'cost' en lugar de 'rent_cost'
        total_cost = sum(
            (assignment.cost or Decimal('0.00')) for assignment in project_assignments
        )
        
        # Si hay campo de mantenimiento, usarlo, sino asumir 0
        total_maintenance = 0
        if hasattr(ProjectResourceItem, 'cost_manteinance'):
            total_maintenance = sum(
                getattr(assignment, 'cost_manteinance', 0) or 0 
                for assignment in project_assignments
            )
        
        return {
            'total_projects': len(project_assignments),
            'active_projects': sum(
                1 for assignment_data in equipment_project_timeline
                if assignment_data['is_current']
            ),
            'historical_projects': sum(
                1 for assignment_data in equipment_project_timeline
                if assignment_data['is_historical']
            ),
            'total_cost': total_cost,
            'total_maintenance_cost': total_maintenance,
            'total_revenue': total_cost + total_maintenance,
        }

    def _get_project_information(self, equipment):
        """Obtiene el historial completo y la ubicación actual del equipo."""
        today = timezone.now().date()
        project_assignments = list(
            ProjectResourceItem.objects.filter(
                resource_item=equipment,
                is_deleted=False,
            ).select_related(
                'project', 'project__partner'
            ).order_by('-operation_start_date', '-id')
        )

        equipment_project_timeline = [
            self._build_assignment_timeline_entry(assignment, today)
            for assignment in project_assignments
        ]
        current_timeline_entries = [
            assignment_data for assignment_data in equipment_project_timeline
            if assignment_data['is_current']
        ]
        future_timeline_entries = sorted(
            (
                assignment_data for assignment_data in equipment_project_timeline
                if assignment_data['is_future']
            ),
            key=lambda assignment_data: assignment_data['operation_start_date'] or today,
        )
        current_assignment = (
            current_timeline_entries[0]['assignment']
            if current_timeline_entries else None
        )

        return {
            'current_assignment': current_assignment,
            'current_assignments': [
                assignment_data['assignment'] for assignment_data in current_timeline_entries
            ],
            'recent_assignments': project_assignments[:5],
            'project_assignments': project_assignments,
            'equipment_project_timeline': equipment_project_timeline,
            'equipment_current_trace': self._build_current_trace(
                equipment,
                current_timeline_entries,
                future_timeline_entries,
                equipment_project_timeline,
            ),
        }

    def _get_maintenance_information(self, equipment, project_information):
        """Obtener información de mantenimiento y estado"""
        today = timezone.now().date()

        # Verificar si hay información de mantenimiento programado
        active_assignments = project_information['current_assignments']

        maintenance_alerts = []
        for assignment in active_assignments:
            if assignment.operation_end_date:
                days_until_end = (assignment.operation_end_date - today).days
                if days_until_end <= 30:
                    maintenance_alerts.append({
                        'type': 'end_project',
                        'message': f'Proyecto termina en {days_until_end} días',
                        'project': assignment.project.partner.name if assignment.project and assignment.project.partner else 'Proyecto sin nombre',
                        'class': 'text-orange-600' if days_until_end > 7 else 'text-red-600'
                    })

        # Estado del equipo (usar campos reales del modelo)
        equipment_status = getattr(equipment, 'stst_status_equipment', None)
        availability_status = getattr(equipment, 'stst_status_disponibility', None)

        status_info = {
            'equipment_status': equipment_status,
            'availability_status': availability_status,
            'equipment_status_class': self._get_status_class(equipment_status),
            'availability_status_class': self._get_status_class(availability_status),
            'needs_attention': equipment_status in ['EN REPARACION', 'DAÑADO', 'INCOMPLETO'],
            'is_available': availability_status in ['DISPONIBLE'],
        }

        return {
            'maintenance_alerts': maintenance_alerts,
            'status_info': status_info,
            'equipment_maintenance_summary': self._get_equipment_maintenance_summary(equipment),
        }

    def _is_assignment_current(self, assignment, today):
        """Determina si una asignación está vigente en la fecha de consulta."""
        if assignment.operation_start_date and assignment.operation_start_date > today:
            return False

        if assignment.operation_end_date and assignment.operation_end_date < today:
            return False

        if assignment.is_retired:
            if assignment.retirement_date and assignment.retirement_date > today:
                return True
            return False

        return True

    def _get_assignment_status(self, assignment, today):
        """Genera un estado legible para el historial operativo."""
        if assignment.operation_start_date and assignment.operation_start_date > today:
            return 'PROGRAMADO'

        if assignment.is_retired:
            if assignment.retirement_date and assignment.retirement_date > today:
                return 'RETIRO PROGRAMADO'
            return 'RETIRADO'

        if assignment.operation_end_date and assignment.operation_end_date < today:
            return 'FINALIZADO'

        return 'EN OPERACION'

    def _get_assignment_badge_class(self, status):
        """Mapa simple de badges para el historial operativo."""
        badge_map = {
            'EN OPERACION': 'badge-info',
            'FINALIZADO': 'badge-success',
            'RETIRADO': 'badge-warning',
            'RETIRO PROGRAMADO': 'badge-warning',
            'PROGRAMADO': 'badge-neutral',
        }
        return badge_map.get(status, 'badge-neutral')

    def _build_assignment_timeline_entry(self, assignment, today):
        """Serializa una asignación para la vista de análisis."""
        status = self._get_assignment_status(assignment, today)
        project = assignment.project
        partner = getattr(project, 'partner', None)

        return {
            'assignment': assignment,
            'project': project,
            'project_id': assignment.project_id,
            'project_name': (
                partner.name if partner else f'Proyecto {assignment.project_id}'
            ),
            'project_location': project.location if project else None,
            'project_is_closed': project.is_closed if project else False,
            'project_url': reverse('project_detail', kwargs={'pk': assignment.project_id}),
            'status': status,
            'status_badge': self._get_assignment_badge_class(status),
            'is_current': self._is_assignment_current(assignment, today),
            'is_future': bool(
                assignment.operation_start_date
                and assignment.operation_start_date > today
            ),
            'is_historical': not self._is_assignment_current(assignment, today) and not bool(
                assignment.operation_start_date
                and assignment.operation_start_date > today
            ),
            'operation_start_date': assignment.operation_start_date,
            'operation_end_date': assignment.operation_end_date,
            'is_retired': assignment.is_retired,
            'retirement_date': assignment.retirement_date,
            'retirement_reason': assignment.retirement_reason,
            'cost': assignment.cost,
        }

    def _build_current_trace(
        self,
        equipment,
        current_timeline_entries,
        future_timeline_entries,
        equipment_project_timeline,
    ):
        """Resume dónde está el equipo al momento de la consulta."""
        fallback_location = getattr(equipment, 'stst_current_location', None)

        if current_timeline_entries:
            current_data = current_timeline_entries[0]
            state = 'EN PROYECTO'
            badge = 'badge-info'
            message = 'Ubicación obtenida desde la asignación operativa vigente.'

            if len(current_timeline_entries) > 1:
                state = 'MULTIPROYECTO'
                badge = 'badge-error'
                message = (
                    f"El equipo aparece en {len(current_timeline_entries)} "
                    'proyectos vigentes. Revisar consistencia.'
                )

            return {
                'state': state,
                'badge': badge,
                'message': message,
                'project_id': current_data['project_id'],
                'project_name': current_data['project_name'],
                'project_url': current_data['project_url'],
                'location': (
                    current_data['project_location']
                    or fallback_location
                    or 'Ubicación no registrada'
                ),
                'operation_start_date': current_data['operation_start_date'],
                'expected_end_date': current_data['operation_end_date'],
                'retirement_date': current_data['retirement_date'],
                'current_project_count': len(current_timeline_entries),
            }

        if future_timeline_entries:
            next_assignment = future_timeline_entries[0]
            return {
                'state': 'PROGRAMADO',
                'badge': 'badge-warning',
                'message': 'Sin asignación activa hoy, pero ya tiene una próxima salida registrada.',
                'project_id': next_assignment['project_id'],
                'project_name': next_assignment['project_name'],
                'project_url': next_assignment['project_url'],
                'location': fallback_location or 'Disponible',
                'operation_start_date': next_assignment['operation_start_date'],
                'expected_end_date': next_assignment['operation_end_date'],
                'retirement_date': next_assignment['retirement_date'],
                'current_project_count': 0,
            }

        last_assignment = next(
            (
                assignment_data for assignment_data in equipment_project_timeline
                if assignment_data['is_historical']
            ),
            None,
        )
        if last_assignment:
            return {
                'state': 'DISPONIBLE',
                'badge': 'badge-success',
                'message': 'No tiene una asignación operativa vigente en la fecha consultada.',
                'project_id': last_assignment['project_id'],
                'project_name': last_assignment['project_name'],
                'project_url': last_assignment['project_url'],
                'location': (
                    fallback_location
                    or last_assignment['project_location']
                    or 'Ubicación no registrada'
                ),
                'operation_start_date': last_assignment['operation_start_date'],
                'expected_end_date': last_assignment['operation_end_date'],
                'retirement_date': last_assignment['retirement_date'],
                'current_project_count': 0,
            }

        return {
            'state': 'SIN HISTORIAL',
            'badge': 'badge-neutral',
            'message': 'El equipo todavía no tiene proyectos asociados registrados.',
            'project_id': None,
            'project_name': None,
            'project_url': None,
            'location': fallback_location or 'Sin ubicación registrada',
            'operation_start_date': None,
            'expected_end_date': None,
            'retirement_date': None,
            'current_project_count': 0,
        }

    def _get_equipment_maintenance_summary(self, equipment):
        """Cruza las hojas de mantenimiento de servicios con el equipo físico."""
        linked_service_assignments = list(
            ProjectResourceItem.objects.filter(
                physical_equipment_code=equipment.id,
                is_deleted=False,
                type_resource='SERVICIO',
            ).select_related(
                'resource_item', 'project', 'project__partner'
            ).order_by('-operation_start_date', '-id')
        )
        assignment_pairs = {
            (assignment.project_id, assignment.resource_item_id)
            for assignment in linked_service_assignments
            if assignment.project_id and assignment.resource_item_id
        }
        service_ids = {
            assignment.resource_item_id for assignment in linked_service_assignments
            if assignment.resource_item_id
        }
        project_ids = {
            assignment.project_id for assignment in linked_service_assignments
            if assignment.project_id
        }

        maintenance_history = []
        total_cost = Decimal('0.00')

        if service_ids and project_ids:
            maintenance_queryset = SheetMaintenance.objects.filter(
                is_deleted=False,
                resource_item_id__in=service_ids,
                id_sheet_project__project_id__in=project_ids,
            ).select_related(
                'resource_item',
                'id_sheet_project',
                'id_sheet_project__project',
                'id_sheet_project__project__partner',
            ).order_by('-start_date', '-sheet_number', '-id')

            for maintenance in maintenance_queryset:
                project = maintenance.id_sheet_project.project
                pair = (project.id, maintenance.resource_item_id)
                if pair not in assignment_pairs:
                    continue

                maintenance_history.append(
                    {
                        'sheet_id': maintenance.id,
                        'sheet_number': maintenance.sheet_number,
                        'project_id': project.id,
                        'project_name': project.partner.name,
                        'project_url': reverse('project_detail', kwargs={'pk': project.id}),
                        'service_name': maintenance.resource_item.name,
                        'service_code': maintenance.resource_item.code,
                        'maintenance_type': maintenance.maintenance_type,
                        'maintenance_type_display': maintenance.get_maintenance_type_display(),
                        'start_date': maintenance.start_date,
                        'end_date': maintenance.end_date,
                        'status': maintenance.status,
                        'location': maintenance.location,
                        'total_days': maintenance.total_days,
                        'cost_total': maintenance.cost_total,
                        'cost_logistics': maintenance.cost_logistics,
                        'maintenance_description': maintenance.maintenance_description,
                    }
                )
                total_cost += maintenance.cost_total or Decimal('0.00')

        return {
            'linked_services_count': len(assignment_pairs),
            'total_maintenances': len(maintenance_history),
            'total_cost': total_cost,
            'last_maintenance_date': (
                maintenance_history[0]['start_date'] if maintenance_history else None
            ),
            'maintenance_history': maintenance_history,
        }

    def _get_status_class(self, status):
        """Obtener clase CSS según el estado del equipo"""
        status_classes = {
            'DISPONIBLE': 'text-green-600',
            'LIBRE': 'text-green-600',
            'RENTADO': 'text-blue-600',
            'EN REPARACION': 'text-red-600',
            'DANADO': 'text-red-600',  # sin tilde por compatibilidad
            'DAÑADO': 'text-red-600',  # con tilde (valor real en modelo)
            'INCOMPLETO': 'text-orange-600',
            'FUERA DE SERVICIO': 'text-gray-600',
            'BUSCAR': 'text-orange-600',
            'INDEFINIDO': 'text-gray-600',
            'STAND BY': 'text-yellow-600',
            'EN ALMACEN': 'text-gray-600',
        }
        return status_classes.get(status, 'text-gray-600')

    def _get_system_metadata(self, equipment):
        """Obtener metadatos del sistema"""
        return {
            'created_info': {
                'date': equipment.created_at,
                'user': equipment.get_create_user(),  # Usar el método de BaseModel
            },
            'updated_info': {
                'date': equipment.updated_at,
                'user': equipment.get_update_user(),  # Usar el método de BaseModel
            },
            'system_info': {
                'version': getattr(equipment, 'version', '1.0'),
                'last_sync': getattr(equipment, 'last_sync', None),
                'system_notes': getattr(equipment, 'system_notes', None),
            }
        }

    def _get_equipment_characteristics(self, equipment):
        """Obtener características específicas del equipo según su subtipo"""
        characteristics = []

        te = getattr(equipment, 'type_equipment', None)

        if te == 'LVMNOS':  # Lavamanos
            if getattr(equipment, 'have_foot_pumps', False):
                characteristics.append('Bombas de Pie')
            if getattr(equipment, 'have_soap_dispenser', False):
                characteristics.append('Dispensador de Jabón')
            if getattr(equipment, 'have_paper_towels', False):
                characteristics.append('Toallas de Papel')

        elif te in ['BTSNHM', 'BTSNMJ']:
            if getattr(equipment, 'have_paper_dispenser', False):
                characteristics.append('Dispensador de Papel')
            if getattr(equipment, 'have_soap_dispenser', False):
                characteristics.append('Dispensador de Jabón')
            if getattr(equipment, 'have_napkin_dispenser', False):
                characteristics.append('Dispensador de Servilletas')
            if getattr(equipment, 'have_urinals', False):
                characteristics.append('Urinarios')
            if getattr(equipment, 'have_seat', False):
                characteristics.append('Asientos')
            if getattr(equipment, 'have_toilet_pump', False):
                characteristics.append('Bomba de Baño')
            if getattr(equipment, 'have_sink_pump', False):
                characteristics.append('Bomba de Lavamanos')
            if getattr(equipment, 'have_toilet_lid', False):
                characteristics.append('Llave de Baño')
            if getattr(equipment, 'have_bathroom_bases', False):
                characteristics.append('Bases de Baño')
            if getattr(equipment, 'have_ventilation_pipe', False):
                characteristics.append('Tubo de Ventilación')

        elif te == 'CMPRBN':
            # CAMPER BAÑO comparte características con batería sanitaria según docs
            if getattr(equipment, 'have_paper_dispenser', False):
                characteristics.append('Dispensador de Papel')
            if getattr(equipment, 'have_soap_dispenser', False):
                characteristics.append('Dispensador de Jabón')
            if getattr(equipment, 'have_napkin_dispenser', False):
                characteristics.append('Dispensador de Servilletas')
            if getattr(equipment, 'have_urinals', False):
                characteristics.append('Urinarios')
            if getattr(equipment, 'have_seat', False):
                characteristics.append('Asientos')
            if getattr(equipment, 'have_toilet_pump', False):
                characteristics.append('Bomba de Baño')
            if getattr(equipment, 'have_sink_pump', False):
                characteristics.append('Bomba de Lavamanos')
            if getattr(equipment, 'have_toilet_lid', False):
                characteristics.append('Llave de Baño')
            if getattr(equipment, 'have_bathroom_bases', False):
                characteristics.append('Bases de Baño')
            if getattr(equipment, 'have_ventilation_pipe', False):
                characteristics.append('Tubo de Ventilación')

        elif te in ['TNQAAC', 'TNQAAR']:
            if getattr(equipment, 'capacity_gallons', None):
                characteristics.append(
                    f'Capacidad: {equipment.capacity_gallons} Galones')

        elif te == 'EST4UR':
            # Solo campos base según docs
            characteristics.append('Estación de 4 Urinarios')

        # Para plantas de tratamiento, mostrar capacidad específica
        elif te in ['PTRTAP', 'PTRTAR']:
            if getattr(equipment, 'plant_capacity', None):
                characteristics.append(
                    f'Capacidad: {equipment.plant_capacity}')

        return {
            'equipment_characteristics': characteristics,
            'has_characteristics': len(characteristics) > 0,
        }

    def _get_special_components(self, equipment):
        """Obtener información de componentes especiales (blower, motor, banda, etc.)"""
        special_subtypes = ['PTRTAP', 'PTRTAR', 'TNQAAC', 'TNQAAR']

        if getattr(equipment, 'type_equipment', None) not in special_subtypes:
            return {'has_special_components': False}

        components = {}

        # Información del Blower
        if equipment.blower_brand or equipment.blower_model:
            components['blower'] = {
                'brand': equipment.blower_brand,
                'model': equipment.blower_model,
            }

        # Información del Motor
        if equipment.engine_brand or equipment.engine_model:
            components['engine'] = {
                'brand': equipment.engine_brand,
                'model': equipment.engine_model,
            }

        # Información de la Banda
        if equipment.belt_brand or equipment.belt_model or equipment.belt_type:
            components['belt'] = {
                'brand': equipment.belt_brand,
                'model': equipment.belt_model,
                'type': equipment.belt_type,
            }

        # Información de Pulleys
        if equipment.blower_pulley_brand or equipment.blower_pulley_model:
            components['blower_pulley'] = {
                'brand': equipment.blower_pulley_brand,
                'model': equipment.blower_pulley_model,
            }

        if equipment.motor_pulley_brand or equipment.motor_pulley_model:
            components['motor_pulley'] = {
                'brand': equipment.motor_pulley_brand,
                'model': equipment.motor_pulley_model,
            }

        # Información del Panel Eléctrico
        if equipment.electrical_panel_brand or equipment.electrical_panel_model:
            components['electrical_panel'] = {
                'brand': equipment.electrical_panel_brand,
                'model': equipment.electrical_panel_model,
            }

        # Información del Guarda Motor (usar campos correctos engine_guard_*)
        if equipment.engine_guard_brand or equipment.engine_guard_model:
            components['motor_guard'] = {
                'brand': equipment.engine_guard_brand,
                'model': equipment.engine_guard_model,
            }

        # Componentes específicos para planta de agua potable
        if getattr(equipment, 'type_equipment', None) == 'PTRTAP':
            potable_components = {}
            if equipment.pump_filter:
                potable_components['pump_filter'] = equipment.pump_filter
            if equipment.pump_pressure:
                potable_components['pump_pressure'] = equipment.pump_pressure
            if equipment.pump_dosing:
                potable_components['pump_dosing'] = equipment.pump_dosing
            if equipment.sand_carbon_filter:
                potable_components['sand_carbon_filter'] = (
                    equipment.sand_carbon_filter
                )
            if equipment.hidroneumatic_tank:
                potable_components['hidroneumatic_tank'] = (
                    equipment.hidroneumatic_tank
                )
            if equipment.uv_filter:
                potable_components['uv_filter'] = equipment.uv_filter
            # Incluir relays si existen (mostrar todo junto en planta potable)
            if equipment.relay_engine:
                potable_components['relay_engine'] = equipment.relay_engine
            if equipment.relay_blower:
                potable_components['relay_blower'] = equipment.relay_blower
            if potable_components:
                components['potable_plant'] = potable_components

        # Componentes planta agua residual (8 campos solicitados)
        if getattr(equipment, 'type_equipment', None) == 'PTRTAR':
            residual_components = {}
            if equipment.pump_filter:
                residual_components['pump_filter'] = equipment.pump_filter
            if equipment.pump_pressure:
                residual_components['pump_pressure'] = equipment.pump_pressure
            if equipment.pump_dosing:
                residual_components['pump_dosing'] = equipment.pump_dosing
            if equipment.sand_carbon_filter:
                residual_components['sand_carbon_filter'] = (
                    equipment.sand_carbon_filter
                )
            if equipment.hidroneumatic_tank:
                residual_components['hidroneumatic_tank'] = (
                    equipment.hidroneumatic_tank
                )
            if equipment.uv_filter:
                residual_components['uv_filter'] = equipment.uv_filter
            if equipment.relay_engine:
                residual_components['relay_engine'] = equipment.relay_engine
            if equipment.relay_blower:
                residual_components['relay_blower'] = equipment.relay_blower
            if residual_components:
                components['residual_relays'] = residual_components

        return {
            'special_components': components,
            'has_special_components': len(components) > 0,
        }

    def _get_capacity_information(self, equipment):
        """Obtener información detallada de capacidad del equipo"""
        # Calcular una representación amigable de la capacidad
        te = getattr(equipment, 'type_equipment', None)
        capacity_display = None
        if te in ['PTRTAP', 'PTRTAR'] and getattr(equipment, 'plant_capacity', None):
            capacity_display = f"{equipment.plant_capacity}"
        elif getattr(equipment, 'capacity_gallons', None):
            capacity_display = f"{equipment.capacity_gallons} gal"

        capacity_info = {
            'capacity_display': capacity_display,
            'capacity_gallons': getattr(equipment, 'capacity_gallons', None),
            'plant_capacity': getattr(equipment, 'plant_capacity', None),
        }

        # Información adicional según el subtipo
        if te in ['PTRTAP', 'PTRTAR']:
            capacity_info['capacity_type'] = 'Capacidad de Planta'
            capacity_info['capacity_unit'] = 'M³/día'
        elif getattr(equipment, 'capacity_gallons', None):
            capacity_info['capacity_type'] = 'Capacidad de Almacenamiento'
            capacity_info['capacity_unit'] = 'Galones'

        return {
            'capacity_info': capacity_info,
        }

    def _get_equipment_status_analysis(self, equipment):
        """Obtener análisis completo del estado del equipo"""
        try:
            # Crear analizador de estado
            analyzer = StatusResourceItem(equipment)
            status_report = analyzer.get_status_report()

            return {
                'status_analysis': status_report,
                'equipment_completeness': {
                    'is_complete': status_report['completeness']['is_complete'],
                    'completion_percentage': status_report['completeness']['completion_percentage'],
                    'missing_items': status_report['completeness']['missing_items'],
                    'missing_count': len(status_report['completeness']['missing_items']),
                },
                'equipment_availability': {
                    'status': status_report['availability']['status'],
                    'current_location': status_report['availability']['current_location'],
                    'commitment_date': status_report['availability']['commitment_date'],
                    'release_date': status_report['availability']['release_date'],
                },
                'project_analysis': status_report.get('project_info'),
                'rental_analysis': status_report.get('rental_info'),
                'inconsistencies_analysis': {
                    'found': status_report['inconsistencies']['found'],
                    'needs_update': status_report['inconsistencies']['needs_update'],
                    'count': len(status_report['inconsistencies']['found']),
                },
                'recommendations': status_report['recommendations'],
                'status_class_mapping': self._get_status_analysis_classes(status_report),
            }
        except Exception as e:
            # En caso de error, devolver información básica
            return {
                'status_analysis': None,
                'equipment_completeness': {
                    'is_complete': False,
                    'completion_percentage': 0,
                    'missing_items': [],
                    'missing_count': 0,
                },
                'equipment_availability': {
                    'status': getattr(equipment, 'stst_status_disponibility', 'DESCONOCIDO'),
                    'current_location': getattr(equipment, 'stst_current_location', None),
                    'commitment_date': getattr(equipment, 'stst_commitment_date', None),
                    'release_date': getattr(equipment, 'stst_release_date', None),
                },
                'project_analysis': None,
                'rental_analysis': None,
                'inconsistencies_analysis': {
                    'found': [],
                    'needs_update': False,
                    'count': 0,
                },
                'recommendations': [f'Error al analizar estado: {str(e)}'],
                'status_class_mapping': {},
            }

    def _get_status_analysis_classes(self, status_report):
        """Obtener clases CSS para los diferentes estados"""
        completeness = status_report['completeness']
        inconsistencies = status_report['inconsistencies']
        availability = status_report['availability']['status']
        
        classes = {
            'completeness_class': 'text-green-600' if completeness['is_complete'] else 'text-red-600',
            'availability_class': self._get_status_class(availability),
            'inconsistencies_class': 'text-red-600' if inconsistencies['needs_update'] else 'text-green-600',
            'completion_badge': 'badge-success' if completeness['is_complete'] else 'badge-error',
            'inconsistencies_badge': 'badge-error' if inconsistencies['needs_update'] else 'badge-success',
        }
        
        # Clase general del estado del equipo
        if completeness['is_complete'] and not inconsistencies['needs_update']:
            classes['overall_status_class'] = 'text-green-600'
            classes['overall_badge'] = 'badge-success'
        elif inconsistencies['needs_update']:
            classes['overall_status_class'] = 'text-red-600'
            classes['overall_badge'] = 'badge-error'
        else:
            classes['overall_status_class'] = 'text-yellow-600'
            classes['overall_badge'] = 'badge-warning'
        
        return classes
