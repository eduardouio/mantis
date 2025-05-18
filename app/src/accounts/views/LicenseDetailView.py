from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from accounts.models import License


class DetailLicense(LoginRequiredMixin, DetailView):
    model = License
    template_name = 'presentations/license_presentation.html'
    context_object_name = 'license'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle de la Licencia {}'.format(
            self.object.license_key
        )
        context['title_page'] = 'Detalle de la Licencia {}'.format(
            self.object.license_key
        )

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        # context['license'] = self.object # 'license' ya está en el contexto por context_object_name
        message = ''
        if context['action'] == 'created':
            message = 'La licencia ha sido creada con éxito.'
        elif context['action'] == 'updated':
            message = 'La licencia ha sido actualizada con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No es posible eliminar la licencia. Existen dependencias.'
        elif context['action'] == 'delete': # Este mensaje parece más para una confirmación previa
            message = 'Esta acción es irreversible. ¿Desea continuar?.'

        context['message'] = message
        return context
