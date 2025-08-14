from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from equipment.models import ResourceItem
from projects.models import ProjectResourceItem


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

        # Estadísticas de uso del equipo
        context.update(self._get_equipment_statistics(equipment))

        # Información de proyectos asociados
        context.update(self._get_project_information(equipment))

        # Información de estado y mantenimiento
        context.update(self._get_maintenance_information(equipment))

        # Metadatos del sistema
        context.update(self._get_system_metadata(equipment))

        # Características específicas del equipo
        context.update(self._get_equipment_characteristics(equipment))

        # Componentes especiales (blower, motor, banda, etc.)
        context.update(self._get_special_components(equipment))

        # Información detallada de capacidad
        context.update(self._get_capacity_information(equipment))

        return context

    def _get_equipment_statistics(self, equipment):
        """Obtener estadísticas del equipo"""
        project_assignments = ProjectResourceItem.objects.filter(
            resource_item=equipment)
        active_assignments = project_assignments.filter(is_active=True)

        # Calcular estadísticas
        total_projects = project_assignments.count()
        active_projects = active_assignments.count()
        total_cost = sum(
            assignment.cost for assignment in project_assignments if assignment.cost)
        total_maintenance_cost = sum(
            assignment.cost_manteinance for assignment in project_assignments if assignment.cost_manteinance)

        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'historical_projects': total_projects - active_projects,
            'total_revenue': total_cost + total_maintenance_cost,
            'total_cost': total_cost,
            'total_maintenance_cost': total_maintenance_cost,
        }

    def _get_project_information(self, equipment):
        """Obtener información de proyectos asociados"""
        project_assignments = ProjectResourceItem.objects.filter(
            resource_item=equipment
        ).select_related('project', 'project__partner').order_by('-start_date')

        current_assignment = project_assignments.filter(is_active=True).first()
        recent_assignments = project_assignments[:5]  # Últimos 5 proyectos

        return {
            'current_assignment': current_assignment,
            'recent_assignments': recent_assignments,
            'project_assignments': project_assignments,
        }

    def _get_maintenance_information(self, equipment):
        """Obtener información de mantenimiento y estado"""
        today = timezone.now().date()

        # Verificar si hay información de mantenimiento programado
        active_assignments = ProjectResourceItem.objects.filter(
            resource_item=equipment,
            is_active=True
        )

        maintenance_alerts = []
        for assignment in active_assignments:
            if assignment.end_date:
                days_until_end = (assignment.end_date - today).days
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
       