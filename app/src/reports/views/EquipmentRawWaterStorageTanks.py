from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from equipment.models.ResourceItem import ResourceItem
from datetime import datetime


class EquipmentRawWaterStorageTanks(TemplateView):
    template_name = 'reports/equipment_raw_water_storage_tanks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment_id = self.kwargs.get('equipment_id')
        
        equipment = get_object_or_404(ResourceItem, id=equipment_id)
        
        if equipment.type_equipment != 'TNQAAC':
            context['error'] = 'Este checklist es solo para Tanques de Almacenamiento de Agua Cruda'
            return context
        
        context['equipment'] = equipment
        context['inspection_date'] = datetime.now().date()
        context['inspector_name'] = (
            self.request.user.get_full_name() or 
            self.request.user.username
        )
        context['observations'] = ''
        
        return context
