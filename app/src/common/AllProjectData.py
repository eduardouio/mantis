"""
Clase para recuperar todos los datos relacionados con un proyecto.

Esta clase proporciona métodos para obtener información completa de un
proyecto, incluyendo equipos asignados, planillas (sheets), y otros
datos relacionados.

Author: Sistema
Date: 2025-10-04
"""

from django.core.exceptions import ObjectDoesNotExist
from projects.models.Project import Project, ProjectResourceItem
from projects.models.SheetProject import SheetProject


class AllProjectData:
    """
    Clase para recuperar y organizar todos los datos de un proyecto.
    
    Attributes:
        project_id (int): ID del proyecto a consultar
        project (Project): Instancia del proyecto
    """
    
    def __init__(self, project_id):
        """
        Inicializa la clase con el ID del proyecto.
        
        Args:
            project_id (int): ID del proyecto a consultar
            
        Raises:
            ObjectDoesNotExist: Si el proyecto no existe
        """
        self.project_id = project_id
        try:
            self.project = Project.objects.get(
                pk=project_id,
                is_active=True
            )
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(
                f"No se encontró el proyecto con ID {project_id}"
            )
    
    def get_assigned_equipment(self):
        """
        Obtiene todos los equipos asignados al proyecto con su detalle
        completo.
        
        Returns:
            list: Lista de diccionarios con información de equipos
        """
        equipment_list = []
        
        project_resources = ProjectResourceItem.objects.filter(
            project=self.project,
            is_active=True
        ).select_related('resource_item')
        
        for pr_item in project_resources:
            resource = pr_item.resource_item
            
            equipment_data = {
                'id': pr_item.id,
                'project_resource_id': pr_item.id,
                'resource_item_id': resource.id,
                'resource_name': resource.name,
                'resource_code': resource.code,
                'resource_type': getattr(resource, 'type_equipment', None),
                'is_service': resource.is_service,
                'rent_cost': float(pr_item.rent_cost),
                'maintenance_cost': float(pr_item.maintenance_cost),
                'maintenance_interval_days': (
                    pr_item.maintenance_interval_days
                ),
                'operation_start_date': (
                    pr_item.operation_start_date.isoformat()
                    if pr_item.operation_start_date else None
                ),
                'operation_end_date': (
                    pr_item.operation_end_date.isoformat()
                    if pr_item.operation_end_date else None
                ),
                'is_retired': pr_item.is_retired,
                'retirement_date': (
                    pr_item.retirement_date.isoformat()
                    if pr_item.retirement_date else None
                ),
                'retirement_reason': pr_item.retirement_reason,
                'created_at': (
                    pr_item.created_at.isoformat()
                    if pr_item.created_at else None
                ),
                'updated_at': (
                    pr_item.updated_at.isoformat()
                    if pr_item.updated_at else None
                ),
            }
            
            # Agregar datos adicionales del recurso si existen
            if hasattr(resource, 'brand'):
                equipment_data['brand'] = resource.brand
            if hasattr(resource, 'model'):
                equipment_data['model'] = resource.model
            if hasattr(resource, 'serial_number'):
                equipment_data['serial_number'] = resource.serial_number
            if hasattr(resource, 'stst_status_equipment'):
                equipment_data['status_equipment'] = (
                    resource.stst_status_equipment
                )
            if hasattr(resource, 'stst_status_disponibility'):
                equipment_data['status_disponibility'] = (
                    resource.stst_status_disponibility
                )
            if hasattr(resource, 'stst_current_location'):
                equipment_data['current_location'] = (
                    resource.stst_current_location
                )
                
            equipment_list.append(equipment_data)
        
        return equipment_list
    
    def get_all_sheets(self):
        """
        Obtiene todas las planillas (SheetProject) asociadas al proyecto.
        Solo incluye los datos de la tabla principal, sin detalles.
        
        Returns:
            list: Lista de diccionarios con información de las planillas
        """
        sheets_list = []
        
        sheets = SheetProject.objects.filter(
            project=self.project,
            is_active=True
        ).order_by('-period_start')
        
        for sheet in sheets:
            sheet_data = {
                'id': sheet.id,
                'project_id': sheet.project.id,
                'issue_date': (
                    sheet.issue_date.isoformat()
                    if sheet.issue_date else None
                ),
                'period_start': (
                    sheet.period_start.isoformat()
                    if sheet.period_start else None
                ),
                'period_end': (
                    sheet.period_end.isoformat()
                    if sheet.period_end else None
                ),
                'status': sheet.status,
                'series_code': sheet.series_code,
                'service_type': sheet.service_type,
                'total_gallons': sheet.total_gallons,
                'total_barrels': sheet.total_barrels,
                'total_cubic_meters': sheet.total_cubic_meters,
                'client_po_reference': sheet.client_po_reference,
                'contact_reference': sheet.contact_reference,
                'contact_phone_reference': sheet.contact_phone_reference,
                'final_disposition_reference': (
                    sheet.final_disposition_reference
                ),
                'invoice_reference': sheet.invoice_reference,
                'subtotal': float(sheet.subtotal),
                'tax_amount': float(sheet.tax_amount),
                'total': float(sheet.total),
                'created_at': (
                    sheet.created_at.isoformat()
                    if sheet.created_at else None
                ),
                'updated_at': (
                    sheet.updated_at.isoformat()
                    if sheet.updated_at else None
                ),
            }
            
            sheets_list.append(sheet_data)
        
        return sheets_list
    
    def get_project_basic_info(self):
        """
        Obtiene la información básica del proyecto.
        
        Returns:
            dict: Diccionario con información básica del proyecto
        """
        return {
            'id': self.project.id,
            'partner_id': self.project.partner.id,
            'partner_name': self.project.partner.name,
            'partner_ruc': self.project.partner.business_tax_id,
            'location': self.project.location,
            'contact_name': self.project.contact_name,
            'contact_phone': self.project.contact_phone,
            'start_date': (
                self.project.start_date.isoformat()
                if self.project.start_date else None
            ),
            'end_date': (
                self.project.end_date.isoformat()
                if self.project.end_date else None
            ),
            'is_closed': self.project.is_closed,
            'created_at': (
                self.project.created_at.isoformat()
                if self.project.created_at else None
            ),
            'updated_at': (
                self.project.updated_at.isoformat()
                if self.project.updated_at else None
            ),
        }
    
    def get_all_data(self):
        """
        Obtiene todos los datos del proyecto en un único diccionario.
        
        Returns:
            dict: Diccionario con toda la información del proyecto organizada
        """
        return {
            'project': self.get_project_basic_info(),
            'assigned_equipment': self.get_assigned_equipment(),
            'sheets': self.get_all_sheets(),
        }


# Función de utilidad para usar directamente
def get_project_data(project_id):
    """
    Función de utilidad para obtener todos los datos de un proyecto.
    
    Args:
        project_id (int): ID del proyecto
        
    Returns:
        dict: Diccionario con toda la información del proyecto
        
    Raises:
        ObjectDoesNotExist: Si el proyecto no existe
    """
    project_data = AllProjectData(project_id)
    return project_data.get_all_data()
