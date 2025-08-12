from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from equipment.models import Vehicle
from equipment.forms import VehicleForm


class VehicleUpdateView(UpdateView):
    model = Vehicle
    template_name = 'forms/vehicle_form.html'
    form_class = VehicleForm

    def get_object(self, queryset=None):
        return get_object_or_404(Vehicle, pk=self.kwargs['pk'], is_active=True)

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Vehículo {form.instance.no_plate} actualizado exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al actualizar el vehículo. Verifique los datos ingresados.'
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = f'Editar Vehículo {self.object.no_plate}'
        context['submit_text'] = 'Actualizar Vehículo'
        context['vehicle'] = self.object  # Conservado si el template lo espera
        return context

    def get_success_url(self):
        return reverse_lazy('vehicle_detail', kwargs={'pk': self.object.pk})
