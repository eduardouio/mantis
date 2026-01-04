from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from equipment.models.ResourceItem import ResourceItem
from datetime import datetime


class EquipmentInfoReport(TemplateView):
    template_name = 'reports/equipment_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment_id = self.kwargs.get('equipment_id')
        
        equipment = get_object_or_404(ResourceItem, id=equipment_id)
        
        # Validar que NO sea un servicio
        if getattr(equipment, 'is_service', False) or equipment.type_equipment == 'SERVIC':
            context['error'] = 'Este reporte es solo para equipos físicos, no para servicios'
            return context
        
        # Datos básicos del equipo
        context['equipment'] = equipment
        context['inspection_date'] = datetime.now().date()
        context['generated_by'] = self.request.user.get_full_name() or self.request.user.username
        
        # Obtener campos organizados
        context['common_fields'] = equipment.present_common_fields
        context['specific_fields'] = equipment.present_specific_fields
        context['have_fields'] = equipment.present_have_fields
        context['state_fields'] = equipment.present_state_fields
        
        # Manejar usuario anónimo de forma segura
        context['report_generated_by'] = (
            self.request.user.get_full_name() 
            if self.request.user.is_authenticated 
            else 'Sistema'
        )
        
        return context
