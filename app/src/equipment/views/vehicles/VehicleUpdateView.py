from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from equipment.models import Vehicle


class VehicleUpdateView(UpdateView):
    model = Vehicle
    template_name = 'equipment/vehicles/vehicle_form.html'
    fields = [
        'brand', 'model', 'type_vehicle', 'year', 'no_plate', 
        'status_vehicle', 'chasis', 'motor_no', 'color', 
        'owner_transport', 'due_date_matricula', 'due_date_cert_oper',
        'date_matricula', 'date_mtop', 'date_technical_review',
        'nro_poliza', 'insurance_company', 'insurance_expiration_date',
        'insurance_issue_date', 'duedate_satellite', 'serial_number',
        'engine_number', 'chassis_number', 'notes', 'is_active'
    ]
    success_url = reverse_lazy('equipment:vehicle_list')
    
    def get_object(self, queryset=None):
        return get_object_or_404(Vehicle, pk=self.kwargs['pk'], is_active=True)
    
    def form_valid(self, form):
        messages.success(self.request, f'Vehículo {form.instance.no_plate} actualizado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el vehículo. Verifique los datos ingresados.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Vehículo {self.object.no_plate}'
        context['submit_text'] = 'Actualizar Vehículo'
        return context
    
    def get_success_url(self):
        return reverse_lazy('equipment:vehicle_detail', kwargs={'pk': self.object.pk})
