from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from equipment.models import Equipment


class ListEquipment(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'lists/equipment_list.html'
    context_object_name = 'equipments'
    ordering = ['name']


class DetailEquipment(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = 'presentations/equipment_presentation.html'
    context_object_name = 'equipment'
