from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from equipment.models import ResourceItem


class ResourceItemDetailView(LoginRequiredMixin, DetailView):
    model = ResourceItem
    template_name = 'presentations/resourse_presentation.html'
    context_object_name = 'equipment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle del Equipo {}'.format(
            self.object.code
        )
        context['title_page'] = 'Detalle del Equipo {}'.format(
            self.object.code
        )

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        context['equipment'] = self.object
        message = ''
        if context['action'] == 'created':
            message = 'El equipo ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El equipo ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No es posible eliminar el equipo. Existen dependencias.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continiar?.'

        context['message'] = message
        return context
