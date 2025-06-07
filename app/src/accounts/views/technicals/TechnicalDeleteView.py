from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from accounts.models import Technical


class TechnicalDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        technical = Technical.objects.get(pk=kwargs['pk'])
        try:
            technical.delete()
            url = reverse_lazy('technical_list')
            return f'{url}?action=deleted'
        except Exception as e:
            # Consider logging the exception e
            url = reverse_lazy('technical_detail', kwargs={'pk': technical.pk})
            return f'{url}?action=no_delete'
