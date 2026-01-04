from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from equipment.models.ResourceItem import ResourceItem
from datetime import datetime


class EquipmentWasherHandsCheck(TemplateView):
    template_name = 'reports/equipment_washer_hands.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment_id = self.kwargs.get('equipment_id')
        
        equipment = get_object_or_404(ResourceItem, id=equipment_id)
        
        context['equipment'] = equipment
        context['inspection_date'] = datetime.now()
        # Manejar usuario anónimo de forma segura
        context['inspector_name'] = (
            self.request.user.get_full_name() 
            if self.request.user.is_authenticated 
            else 'Sistema'
        )
        
        return context
