from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
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


class DetailEquipment(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = 'presentations/equipment_presentation.html'
    context_object_name = 'equipment'


class CreateEquipment(LoginRequiredMixin, CreateView):
    model = Equipment
    template_name = 'forms/equipment_form.html'
    form_class = EquipmentForm
    success_url = '/equipos/'

    def get_success_url(self):
        url = reverse_lazy('equipment_detail', kwargs={'pk': self.object.pk})
        return url
