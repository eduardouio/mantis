from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from accounts.models import License
from accounts.forms import LicenceForm # Importar desde accounts.forms


class LicenseUpdateView(LoginRequiredMixin, UpdateView):
    model = License
    template_name = 'forms/license_form.html'
    form_class = LicenceForm
    # success_url = '/licencias/' # Reemplazado por get_success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Licencia {}'.format(
            self.object.license_key
        )
        context['title_page'] = 'Actualizar Licencia {}'.format(
            self.object.license_key
        )
        return context

    def get_success_url(self):
        url = reverse_lazy('license_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url
