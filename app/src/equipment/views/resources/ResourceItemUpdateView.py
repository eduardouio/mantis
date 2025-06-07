from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from equipment.models import ResourceItem
from equipment.forms.ResourceItemForm import ResourceItemForm


class ResourceItemUpdateView(LoginRequiredMixin, UpdateView):
    model = ResourceItem
    template_name = 'forms/equipment_form.html'
    form_class = ResourceItemForm
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
        url = reverse_lazy('resource_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url
