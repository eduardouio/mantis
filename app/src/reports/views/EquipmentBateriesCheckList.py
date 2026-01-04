from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from equipment.models.ResourceItem import ResourceItem


class EquipmentBateriesCheckList(TemplateView):
    template_name = 'reports/equipment_bateries.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment_id = self.kwargs.get('equipment_id')
        
        equipment = get_object_or_404(ResourceItem, id=equipment_id)
        
        # Validar que sea batería sanitaria
        valid_types = ['BTSNHM', 'BTSNMJ']
        if equipment.type_equipment not in valid_types:
            context['error'] = 'Este checklist es solo para Baterías Sanitarias (Hombre/Mujer)'
            return context
        
        # Datos del equipo
        context['equipment'] = equipment
        
        # Fecha de inspección (hoy)
        from datetime import datetime
        context['inspection_date'] = datetime.now().date()
        
        # Inspector (usuario actual)
        context['inspector_name'] = (
            self.request.user.get_full_name() or 
            self.request.user.username
        )
        
        # Observaciones (vacío por defecto)
        context['observations'] = ''
        
        return context
