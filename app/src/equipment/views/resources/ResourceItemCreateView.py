from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from equipment.models import ResourceItem
from equipment.forms.ResourceItemForm import ResourceItemForm


class ResourceItemCreateView(LoginRequiredMixin, CreateView):
    model = ResourceItem
    template_name = 'forms/equipment_form.html'
    form_class = ResourceItemForm
    success_url = '/equipos/'

    def get_success_url(self):
        url = reverse_lazy('resource_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nuevo Equipo'
        context['title_page'] = 'Registrar Nuevo Equipo'
        return context
