from django.http import JsonResponse
from django.views import View
from projects.models.CustodyChain import ChainCustodyDetail
from equipment.models.ResourceItem import ResourceItem


class RegenerateEquipmentCodesAPI(View):
    """API para regenerar códigos de equipos en detalles de cadenas de custodia existentes."""

    def get_equipment_code_and_abbreviation(self, project_resource):
        """Obtiene el código completo y la abreviatura del equipo."""
        try:
            physical_code = project_resource.physical_equipment_code
            if not physical_code:
                return None, None
            
            resource_item = ResourceItem.objects.filter(
                id=physical_code,
                is_active=True
            ).first()
            
            if not resource_item or not resource_item.code:
                return None, None
            
            code_equipment = resource_item.code
            parts = code_equipment.split('-')
            equipment_abbreviation = parts[1] if len(parts) > 1 else None
            
            return code_equipment, equipment_abbreviation
        except Exception:
            return None, None

    def post(self, request):
        """Regenerar códigos de equipos para todos los detalles activos."""
        try:
            details = ChainCustodyDetail.objects.filter(is_active=True).select_related('project_resource')
            
            updated_count = 0
            skipped_count = 0
            
            for detail in details:
                code_equipment, equipment_abbr = self.get_equipment_code_and_abbreviation(detail.project_resource)
                
                if code_equipment or equipment_abbr:
                    detail.code_equipment = code_equipment
                    detail.equipment = equipment_abbr
                    detail.save(update_fields=['code_equipment', 'equipment', 'updated_at'])
                    updated_count += 1
                else:
                    skipped_count += 1
            
            return JsonResponse({
                "success": True,
                "message": f"Códigos regenerados exitosamente",
                "updated": updated_count,
                "skipped": skipped_count
            })
            
        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error al regenerar códigos: {str(e)}"},
                status=500
            )
