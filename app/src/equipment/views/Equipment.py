from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    RedirectView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from equipment.models import Equipment

from django import forms


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'name', 'brand', 'model', 'code', 'date_purchase', 'height',
            'width', 'depth', 'weight', 'description', 'status', 'is_active',
            'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'brand': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'model': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'code': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'date_purchase': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'height': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'width': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'depth': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'description': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'notes': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'status': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ListEquipment(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'lists/equipment_list.html'
    context_object_name = 'equipments'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado De Equipos Registrados'
        context['title_page'] = 'Listado De Equipos'

        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'El equipo ha sido eliminado con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context


class DetailEquipment(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = 'presentations/equipment_presentation.html'
    context_object_name = 'equipment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle del Equipo {}'.format(
            self.object.code
        )
        context['title_page'] = 'Detalle del Equipo {}'.format(
            self.object.code
        )

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        context['equipment'] = self.object
        message = ''
        if context['action'] == 'created':
            message = 'El equipo ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El equipo ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No es posible eliminar el equipo. Existen dependencias.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continiar?.'

        context['message'] = message
        return context


class CreateEquipment(LoginRequiredMixin, CreateView):
    model = Equipment
    template_name = 'forms/equipment_form.html'
    form_class = EquipmentForm
    success_url = '/equipos/'

    def get_success_url(self):
        url = reverse_lazy('equipment_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nuevo Equipo'
        context['title_page'] = 'Registrar Nuevo Equipo'
        return context


class UpdateEquipment(LoginRequiredMixin, UpdateView):
    model = Equipment
    template_name = 'forms/equipment_form.html'
    form_class = EquipmentForm
    success_url = '/equipos/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Equipo {}'.format(
            self.object.code
        )
        context['title_page'] = 'Actualizar Equipo {}'.format(
            self.object.code
        )
        return context

    def get_success_url(self):
        url = reverse_lazy('equipment_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url


class DeleteEquipment(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        equipment = Equipment.objects.get(pk=kwargs['pk'])
        try:
            equipment.delete()
            url = reverse_lazy('equipment_list')
            return f'{url}?action=deleted'
        except Exception as e:
            url = reverse_lazy('equipment_detail', kwargs={'pk': equipment.pk})
            return f'{url}?action=no_delete'