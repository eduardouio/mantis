import json
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Partner
from projects.forms.PartnerForm import PartnerForm
from equipment.models import Vehicle
from accounts.models import Technical


class PartnerUpdateView(LoginRequiredMixin, UpdateView):
    model = Partner
    template_name = 'forms/partner_form.html'
    form_class = PartnerForm
    success_url = '/socios/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Socio de Negocio {}'.format(
            self.object.business_tax_id
        )
        context['title_page'] = 'Actualizar Socio de Negocio {}'.format(
            self.object.business_tax_id
        )
        vehicles = Vehicle.get_true_false_list(self.object)
        technicals = Technical.get_true_false_list(self.object)

        context['vehicles'] = json.dumps(vehicles)
        context['technicals'] = json.dumps(technicals)
        return context

    def get_success_url(self):
        url = reverse_lazy('partner_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url
