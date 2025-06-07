from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from equipment.models import ResourceItem


class ResourceItemDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        equipment = ResourceItem.objects.get(pk=kwargs['pk'])
        try:
            equipment.delete()
            url = reverse_lazy('resource_list')
            return f'{url}?action=deleted'
        except Exception as e:
            url = reverse_lazy('resource_detail', kwargs={'pk': equipment.pk})
            return f'{url}?action=no_delete'
