from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from accounts.models import Technical
from accounts.forms import TechnicalForm


class UpdateTechnical(LoginRequiredMixin, UpdateView):
    model = Technical
    template_name = 'forms/technical_form.html'
    form_class = TechnicalForm
    # success_url = '/tecnicos/' # Se reemplaza por get_success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Técnico {}'.format(
            self.object.first_name)
        context['title_page'] = 'Actualizar Técnico {}'.format(
            self.object.first_name)
        return context

    def get_success_url(self):
        url = reverse_lazy('technical_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url
