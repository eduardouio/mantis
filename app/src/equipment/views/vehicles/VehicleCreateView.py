from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from equipment.models import Vehicle
from equipment.forms import VehicleForm


class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    template_name = 'forms/vehicle_form.html'
    form_class = VehicleForm

    def get_success_url(self):
        messages.success(
            self.request,
            f'Vehículo {self.object.no_plate} creado exitosamente.'
        )
        url = reverse_lazy('vehicle_detail', kwargs={'pk': self.object.pk})
        return f'{url}?action=created'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nuevo Vehículo'
        context['title_page'] = 'Registrar Nuevo Vehículo'
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            'El vehículo ha sido creado correctamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al crear el vehículo. Verifique los datos.'
        )
        return super().form_invalid(form)
