from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from equipment.models import Vehicle


class VehicleCreateView(CreateView):
    model = Vehicle
    template_name = 'forms/vehicle_form.html'
    fields = [
        'brand', 'model', 'type_vehicle', 'year', 'no_plate',
        'status_vehicle', 'chassis_number', 'engine_number', 'color',
        'owner_transport', 'due_date_matricula', 'due_date_cert_oper',
        'date_matricula', 'date_mtop', 'date_technical_review',
        'nro_poliza', 'insurance_company', 'insurance_expiration_date',
        'insurance_issue_date', 'duedate_satellite', 'serial_number',
        'notes'
    ]
    success_url = reverse_lazy('equipment:vehicle_list')

    def form_valid(self, form):
        messages.success(
            self.request, f'Vehículo {form.instance.no_plate} creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, 'Error al crear el vehículo. Verifique los datos ingresados.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Vehículo'
        context['submit_text'] = 'Crear Vehículo'
        return context
