from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from accounts.models import License

class ListLicense(LoginRequiredMixin, ListView):
    model = License
    template_name = 'lists/license_list.html'
    context_object_name = 'licenses'
    ordering = ['license_key']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado De Licencias Registradas'
        context['title_page'] = 'Listado De Licencias'

        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'La licencia ha sido eliminada con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context
