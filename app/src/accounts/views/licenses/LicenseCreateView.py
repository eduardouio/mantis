from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from accounts.models import License
from accounts.forms import LicenceForm


class LicenseCreateView(LoginRequiredMixin, CreateView):
    model = License
    template_name = 'forms/license_form.html'
    form_class = LicenceForm
    # success_url = '/licencias/' # Reemplazado por ge
    # t_success_url

    def get_success_url(self):
        url = reverse_lazy('license_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url

    def get_context_data(self, **kwargs): # Añadir para consistencia
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nueva Licencia'
        context['title_page'] = 'Registrar Nueva Licencia'
        return context
