from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db import transaction
from equipment.models import Vehicle, CertificationVehicle, PassVehicle
from equipment.forms import VehicleForm
import json


class VehicleUpdateView(UpdateView):
    model = Vehicle
    template_name = 'forms/vehicle_form.html'
    form_class = VehicleForm
    success_url = reverse_lazy('vehicle_list')

    def get_object(self, queryset=None):
        return get_object_or_404(Vehicle, pk=self.kwargs['pk'], is_active=True)

    @transaction.atomic
    def form_valid(self, form):
        """Guardar el vehículo y procesar datos adicionales de certificaciones y pases"""
        # Actualizar el vehículo
        response = super().form_valid(form)
        
        # Eliminar certificaciones y pases existentes
        CertificationVehicle.objects.filter(vehicle=self.object).delete()
        PassVehicle.objects.filter(vehicle=self.object).delete()

        # Procesar certificaciones desde el request
        certifications_data = self.request.POST.get('certifications_data')
        if certifications_data:
            try:
                certifications = json.loads(certifications_data)
                self.create_certifications(certifications)
            except json.JSONDecodeError:
                pass

        # Procesar pases desde el request
        passes_data = self.request.POST.get('passes_data')
        if passes_data:
            try:
                passes = json.loads(passes_data)
                self.create_passes(passes)
            except json.JSONDecodeError:
                pass

        messages.success(
            self.request, f'Vehículo {form.instance.no_plate} actualizado exitosamente.')
        return response

    def create_certifications(self, certifications_data):
        """Crear certificaciones para el vehículo"""
        for certification_data in certifications_data:
            CertificationVehicle.objects.create(
                vehicle=self.object,
                name=certification_data.get('name'),
                date_start=certification_data.get('date_start'),
                date_end=certification_data.get('date_end'),
                description=certification_data.get('description') or None,
                is_active=True
            )

    def create_passes(self, passes_data):
        """Crear pases para el vehículo"""
        for pass_data in passes_data:
            PassVehicle.objects.create(
                vehicle=self.object,
                bloque=pass_data.get('bloque'),
                fecha_caducidad=pass_data.get('fecha_caducidad')
            )

    def form_invalid(self, form):
        messages.error(
            self.request, 'Error al actualizar el vehículo. Verifique los datos ingresados.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = f'Editar Vehículo {self.object.no_plate}'
        context['submit_text'] = 'Actualizar Vehículo'
        context['vehicle'] = self.object
        return context

    def get_success_url(self):
        return reverse_lazy('vehicle_detail', kwargs={'pk': self.object.pk})
