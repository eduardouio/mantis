from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from equipment.models import Vehicle


class VehicleDeleteView(DeleteView):
    model = Vehicle
    template_name = 'equipment/vehicles/vehicle_confirm_delete.html'
    context_object_name = 'vehicle'
    success_url = reverse_lazy('equipment:vehicle_list')
    
    def get_object(self, queryset=None):
        return get_object_or_404(Vehicle, pk=self.kwargs['pk'], is_active=True)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        
        # Usar el método delete personalizado del BaseModel (soft delete)
        self.object.delete()
        
        messages.success(
            self.request, 
            f'Vehículo {self.object.no_plate} eliminado exitosamente.'
        )
        
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Eliminar Vehículo {self.object.no_plate}'
        
        # Verificar si el vehículo tiene certificaciones o pases asociados
        from equipment.models.CertificationVehicle import CertificationVehicle
        from equipment.models.PassVehicle import PassVehicle
        
        context['has_certifications'] = CertificationVehicle.objects.filter(
            vehicle=self.object, is_active=True
        ).exists()
        
        context['has_passes'] = PassVehicle.objects.filter(
            vehicle=self.object
        ).exists()
        
        return context
