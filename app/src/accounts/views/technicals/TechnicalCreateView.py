from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from accounts.models import Technical
from accounts.forms import TechnicalForm


class TechnicalCreateView(LoginRequiredMixin, CreateView):
    model = Technical
    template_name = 'forms/technical_form.html'
    form_class = TechnicalForm
    success_url = reverse_lazy('technical_list')

    def get_success_url(self):
        url = reverse_lazy('technical_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nuevo Técnico'
        context['title_page'] = 'Registrar Nuevo Técnico'
        return context
