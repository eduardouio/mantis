from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from accounts.models import License

class DeleteLicense(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        license_obj = License.objects.get(pk=kwargs['pk']) # Renombrar variable para evitar conflicto con el modelo
        try:
            license_obj.delete()
            url = reverse_lazy('license_list')
            return f'{url}?action=deleted'
        except Exception as e:
            # Considerar logging e
            url = reverse_lazy('license_detail', kwargs={'pk': license_obj.pk})
            return f'{url}?action=no_delete'
