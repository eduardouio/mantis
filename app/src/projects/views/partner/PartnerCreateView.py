from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Partner
from projects.forms.PartnerForm import PartnerForm


class PartnerCreateView(LoginRequiredMixin, CreateView):
    model = Partner
    template_name = 'forms/partner_form.html'
    form_class = PartnerForm
    success_url = '/socios/'

    def get_success_url(self):
        url = reverse_lazy('partner_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nuevo Socio de Negocio'
        context['title_page'] = 'Registrar Nuevo Socio de Negocio'
        return context
