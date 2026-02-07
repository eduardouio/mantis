"""
Clase para verificar la disponibilidad de equipos y detectar inconsistencias
entre el estado de los recursos y su asignación en proyectos activos.
"""

from equipment.models import ResourceItem
from projects.models import Project, ProjectResourceItem


class CheckAvailableResources:
    """
    Verifica la consistencia entre el estado de disponibilidad de los equipos
    y su asignación real en proyectos activos.
    """

    def __init__(self):
        self.inconsistencies = []
        self.equipments_checked = 0

    def check_all_equipments(self):
        """
        Verifica todos los equipos (no servicios) del sistema.
        
        Returns:
            dict: Diccionario con los resultados de la verificación
        """
        # Obtener solo equipos activos (no servicios)
        equipments = ResourceItem.objects.filter(
            is_active=True,
            type_equipment__isnull=False
        ).exclude(type_equipment='SERVIC')

        self.equipments_checked = equipments.count()
        self.inconsistencies = []

        for equipment in equipments:
            self._check_equipment(equipment)

        return self._generate_report()

    def check_equipment_by_id(self, equipment_id):
        """
        Verifica un equipo específico por su ID.
        
        Args:
            equipment_id (int): ID del equipo a verificar
            
        Returns:
            dict: Resultado de la verificación para ese equipo
        """
        try:
            equipment = ResourceItem.objects.get(
                id=equipment_id,
                is_active=True,
                type_equipment__isnull=False
            )
            
            if equipment.type_equipment == 'SERVIC':
                return {
                    'success': False,
                    'error': 'No se puede verificar servicios, solo equipos físicos'
                }
            
            self.equipments_checked = 1
            self.inconsistencies = []
            self._check_equipment(equipment)
            
            return self._generate_report()
            
        except ResourceItem.DoesNotExist:
            return {
                'success': False,
                'error': f'Equipo con ID {equipment_id} no encontrado'
            }

    def _check_equipment(self, equipment):
        """
        Verifica un equipo individual.
        
        Args:
            equipment (ResourceItem): Instancia del equipo a verificar
        """
        # Buscar si el equipo está en algún proyecto activo
        active_projects = ProjectResourceItem.objects.filter(
            resource_item=equipment,
            type_resource='EQUIPO',
            is_active=True,
            is_retired=False,
            project__is_closed=False,
            project__is_deleted=False
        ).select_related('project')

        is_in_active_project = active_projects.exists()
        current_status = equipment.stst_status_disponibility

        # Detectar inconsistencias
        if is_in_active_project and current_status == 'DISPONIBLE':
            # El equipo está en un proyecto activo pero marcado como disponible
            self.inconsistencies.append({
                'equipment_id': equipment.id,
                'equipment_code': equipment.code,
                'equipment_name': equipment.name,
                'type': 'INCONSISTENCIA',
                'issue': 'MARCADO_DISPONIBLE_PERO_RENTADO',
                'current_status': current_status,
                'expected_status': 'RENTADO',
                'projects': [
                    {
                        'project_id': pr.project.id,
                        'project_name': str(pr.project),
                        'start_date': pr.operation_start_date.isoformat() if pr.operation_start_date else None,
                        'end_date': pr.operation_end_date.isoformat() if pr.operation_end_date else None
                    }
                    for pr in active_projects
                ],
                'recommendation': 'Cambiar estado a RENTADO'
            })
            
        elif not is_in_active_project and current_status == 'RENTADO':
            # El equipo está marcado como rentado pero no está en ningún proyecto activo
            self.inconsistencies.append({
                'equipment_id': equipment.id,
                'equipment_code': equipment.code,
                'equipment_name': equipment.name,
                'type': 'INCONSISTENCIA',
                'issue': 'MARCADO_RENTADO_PERO_DISPONIBLE',
                'current_status': current_status,
                'expected_status': 'DISPONIBLE',
                'projects': [],
                'stored_project_id': equipment.stst_current_project_id,
                'stored_location': equipment.stst_current_location,
                'recommendation': 'Cambiar estado a DISPONIBLE y limpiar datos de proyecto'
            })

    def _generate_report(self):
        """
        Genera el reporte final de la verificación.
        
        Returns:
            dict: Reporte con los resultados
        """
        return {
            'success': True,
            'equipments_checked': self.equipments_checked,
            'inconsistencies_found': len(self.inconsistencies),
            'inconsistencies': self.inconsistencies,
            'summary': {
                'marked_available_but_rented': len([
                    i for i in self.inconsistencies 
                    if i['issue'] == 'MARCADO_DISPONIBLE_PERO_RENTADO'
                ]),
                'marked_rented_but_available': len([
                    i for i in self.inconsistencies 
                    if i['issue'] == 'MARCADO_RENTADO_PERO_DISPONIBLE'
                ])
            }
        }

    def fix_inconsistency(self, equipment_id):
        """
        Corrige automáticamente la inconsistencia de un equipo.
        
        Args:
            equipment_id (int): ID del equipo a corregir
            
        Returns:
            dict: Resultado de la corrección
        """
        try:
            equipment = ResourceItem.objects.get(id=equipment_id)
            
            # Verificar el estado actual
            active_projects = ProjectResourceItem.objects.filter(
                resource_item=equipment,
                type_resource='EQUIPO',
                is_active=True,
                is_retired=False,
                project__is_closed=False,
                project__is_deleted=False
            ).select_related('project')

            is_in_active_project = active_projects.exists()

            if is_in_active_project:
                # Debe estar marcado como RENTADO
                project = active_projects.first().project
                equipment.stst_status_disponibility = 'RENTADO'
                equipment.stst_current_project_id = project.id
                equipment.stst_current_location = project.location
                equipment.save()
                
                return {
                    'success': True,
                    'message': f'Equipo {equipment.code} actualizado a RENTADO',
                    'new_status': 'RENTADO',
                    'project_id': project.id
                }
            else:
                # Debe estar marcado como DISPONIBLE
                equipment.stst_status_disponibility = 'DISPONIBLE'
                equipment.stst_current_project_id = None
                equipment.stst_current_location = None
                equipment.stst_commitment_date = None
                equipment.save()
                
                return {
                    'success': True,
                    'message': f'Equipo {equipment.code} actualizado a DISPONIBLE',
                    'new_status': 'DISPONIBLE'
                }
                
        except ResourceItem.DoesNotExist:
            return {
                'success': False,
                'error': f'Equipo con ID {equipment_id} no encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def fix_all_inconsistencies(self):
        """
        Corrige automáticamente todas las inconsistencias encontradas.
        
        Returns:
            dict: Resultado de la corrección masiva
        """
        # Primero verificar todos los equipos
        report = self.check_all_equipments()
        
        if report['inconsistencies_found'] == 0:
            return {
                'success': True,
                'message': 'No se encontraron inconsistencias',
                'fixed': 0
            }
        
        fixed_count = 0
        errors = []
        
        for inconsistency in self.inconsistencies:
            result = self.fix_inconsistency(inconsistency['equipment_id'])
            if result['success']:
                fixed_count += 1
            else:
                errors.append({
                    'equipment_id': inconsistency['equipment_id'],
                    'error': result['error']
                })
        
        return {
            'success': True,
            'total_inconsistencies': report['inconsistencies_found'],
            'fixed': fixed_count,
            'errors': errors
        }
