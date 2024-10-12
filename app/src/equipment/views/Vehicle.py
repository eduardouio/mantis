from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, RedirectView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from equipment.models import Vehicle
from django import forms


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'name', 'brand', 'code_vehicle', 'model', 'type_vehicle', 'year',
            'no_plate', 'owner_transport', 'is_active', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'brand': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'code_vehicle': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'model': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'type_vehicle': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'year': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'no_plate': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'owner_transport': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
        }


class ListVehicle(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'lists/vehicle_list.html'
    context_object_name = 'vehicles'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Vehículos Registrados'
        context['title_page'] = 'Listado de Vehículos'

        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'El vehículo ha sido eliminado con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context


class DetailVehicle(LoginRequiredMixin, DetailView):
    model = Vehicle
    template_name = 'presentations/vehicle_presentation.html'
    context_object_name = 'vehicle'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle del Vehículo {}'.format(
            self.object.no_plate
        )
        context['title_page'] = 'Detalle del Vehículo {}'.format(
            self.object.no_plate
        )

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        context['vehicle'] = self.object
        message = ''
        if context['action'] == 'created':
            message = 'El vehículo ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El vehículo ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No es posible eliminar el vehículo. Existen dependencias.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'
        elif context['action'] == 'popup_window':
            context['popup_window'] = True

        context['message'] = message
        return context


class CreateVehicle(LoginRequiredMixin, CreateView):
    model = Vehicle
    template_name = 'forms/vehicle_form.html'
    form_class = VehicleForm
    success_url = '/vehiculos/'

    def get_success_url(self):
        url = reverse_lazy('vehicle_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url


class UpdateVehicle(LoginRequiredMixin, UpdateView):
    model = Vehicle
    template_name = 'forms/vehicle_form.html'
    form_class = VehicleForm
    success_url = '/vehiculos/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Vehículo {}'.format(
            self.object.no_plate
        )
        context['title_page'] = 'Actualizar Vehículo {}'.format(
            self.object.no_plate
        )
        return context

    def get_success_url(self):
        url = reverse_lazy('vehicle_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url


class DeleteVehicle(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        vehicle = Vehicle.objects.get(pk=kwargs['pk'])
        try:
            vehicle.delete()
            url = reverse_lazy('vehicle_list')
            return f'{url}?action=deleted'
        except Exception as e:
            return f'{reverse_lazy("vehicle_detail", kwargs={"pk": kwargs["pk"]})}?action=no_delete'
