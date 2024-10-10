from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from equipment.models import Equipment


class ListEquipment(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'lists/equipment.html'
    context_object_name = 'equipments'
    ordering = ['name']
