"""
Generador de calendario de mantenimientos para todos los proyectos activos.
Basado en frequency_type: DAY (intervalo), WEEK (días semana), MONTH (días mes)
"""

from datetime import date, timedelta
from calendar import monthrange
from projects.models.Project import Project, ProjectResourceItem


class MaintenanceScheduler:
    """Genera calendario de mantenimientos para proyectos activos."""

    @staticmethod
    def get_month_calendar(year: int, month: int) -> dict:
        """
        Genera el calendario de mantenimientos para un mes específico.
        
        Args:
            year: Año del calendario
            month: Mes del calendario (1-12)
            
        Returns:
            dict con estructura del calendario y mantenimientos
        """
        first_day = date(year, month, 1)
        days_in_month = monthrange(year, month)[1]
        last_day = date(year, month, days_in_month)
        
        # Obtener todos los recursos de proyectos activos
        resources = ProjectResourceItem.objects.filter(
            project__is_closed=False,
            is_active=True,
            is_retired=False,
            is_deleted=False,
            type_resource='SERVICIO'  # Solo servicios, no equipos
        ).select_related('project', 'project__partner', 'resource_item')
        
        # Generar mantenimientos por fecha
        maintenance_by_date = {}
        
        for resource in resources:
            dates = MaintenanceScheduler._generate_dates(
                resource, first_day, last_day
            )
            
            for maint_date in dates:
                date_str = maint_date.isoformat()
                if date_str not in maintenance_by_date:
                    maintenance_by_date[date_str] = []
                
                maintenance_by_date[date_str].append({
                    'id': resource.id,
                    'code': resource.resource_item.code,
                    'name': resource.resource_item.name,
                    'description': resource.detailed_description,
                    'cost': float(resource.cost),
                    'frequency_type': resource.frequency_type,
                    'interval_days': resource.interval_days,
                    'project_id': resource.project.id,
                    'project_name': resource.project.partner.name,
                    'project_location': resource.project.location or '',
                    'project_cardinal': resource.project.cardinal_point or '',
                })
        
        # Generar estructura de semanas
        weeks = MaintenanceScheduler._generate_weeks(
            year, month, days_in_month, first_day, maintenance_by_date
        )
        
        # Calcular resumen
        all_maintenances = []
        for date_list in maintenance_by_date.values():
            all_maintenances.extend(date_list)
        
        total_cost = sum(m['cost'] for m in all_maintenances)
        unique_resources = len(set(m['id'] for m in all_maintenances))
        unique_projects = len(set(m['project_id'] for m in all_maintenances))
        
        return {
            'year': year,
            'month': month,
            'month_name': first_day.strftime('%B'),
            'weeks': weeks,
            'maintenance_by_date': maintenance_by_date,
            'summary': {
                'total_maintenances': len(all_maintenances),
                'total_cost': total_cost,
                'resources_count': unique_resources,
                'projects_count': unique_projects,
            }
        }
    
    @staticmethod
    def _generate_dates(resource, start_date: date, end_date: date) -> list:
        """Genera las fechas de mantenimiento según el tipo de frecuencia."""
        dates = []
        freq_type = resource.frequency_type
        
        # Usar la fecha más reciente entre operation_start_date y start_date
        op_start = resource.operation_start_date
        actual_start = max(op_start, start_date) if op_start else start_date
        
        if freq_type == 'DAY':
            # Intervalo de días
            interval = resource.interval_days if resource.interval_days > 0 else 1
            
            # Calcular la primera fecha de mantenimiento dentro del rango
            if op_start and op_start < actual_start:
                days_diff = (actual_start - op_start).days
                remainder = days_diff % interval
                if remainder > 0:
                    first_maint = actual_start + timedelta(days=(interval - remainder))
                else:
                    first_maint = actual_start
            else:
                first_maint = actual_start
            
            current = first_maint
            while current <= end_date:
                dates.append(current)
                current += timedelta(days=interval)
                
        elif freq_type == 'WEEK':
            # Días específicos de la semana
            weekdays = resource.weekdays or []
            if not weekdays:
                return dates
            
            current = actual_start
            while current <= end_date:
                # Python: Monday=0, Sunday=6
                if current.weekday() in weekdays:
                    dates.append(current)
                current += timedelta(days=1)
                
        elif freq_type == 'MONTH':
            # Días específicos del mes
            monthdays = resource.monthdays or []
            if not monthdays:
                return dates
            
            current = actual_start
            while current <= end_date:
                if current.day in monthdays:
                    dates.append(current)
                current += timedelta(days=1)
        
        return dates
    
    @staticmethod
    def _generate_weeks(year: int, month: int, days_in_month: int, 
                        first_day: date, maintenance_by_date: dict) -> list:
        """Genera la estructura de semanas del calendario."""
        weeks = []
        today = date.today()
        
        # Día de la semana del primer día (0=Lunes en nuestra convención)
        # Python: Monday=0, Sunday=6 - ya está correcto
        start_day_of_week = first_day.weekday()
        
        current_week = []
        
        # Días vacíos al inicio
        for _ in range(start_day_of_week):
            current_week.append(None)
        
        # Días del mes
        for day in range(1, days_in_month + 1):
            current_date = date(year, month, day)
            date_str = current_date.isoformat()
            maintenances = maintenance_by_date.get(date_str, [])
            
            current_week.append({
                'day': day,
                'date': date_str,
                'is_today': current_date == today,
                'maintenances': maintenances,
                'has_maintenances': len(maintenances) > 0,
                'count': len(maintenances),
            })
            
            # Si es domingo (6), nueva semana
            if len(current_week) == 7:
                weeks.append(current_week)
                current_week = []
        
        # Días vacíos al final
        if current_week:
            while len(current_week) < 7:
                current_week.append(None)
            weeks.append(current_week)
        
        return weeks
