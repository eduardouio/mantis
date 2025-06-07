from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from accounts.models import Technical


class TechnicalListView(LoginRequiredMixin, ListView):
    model = Technical
    template_name = 'lists/technical_list.html'
    context_object_name = 'technicals'
    ordering = ['first_name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Técnicos'
        context['title_page'] = 'Listado de Técnicos'

        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'El técnico ha sido eliminado con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context
