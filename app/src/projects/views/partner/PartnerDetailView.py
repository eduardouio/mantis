from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Partner, Project


class PartnerDetailView(LoginRequiredMixin, DetailView):
    model = Partner
    template_name = 'presentations/partner_presentation.html'
    context_object_name = 'partner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle del Socio de Negocio {}'.format(
            self.object.business_tax_id
        )
        context['title_page'] = 'Detalle del Socio de Negocio {}'.format(
            self.object.business_tax_id
        )
        
        # Agregar proyectos asociados al contexto
        context['projects'] = Project.objects.filter(
            partner=self.object,
            is_active=True
        ).order_by('-created_at')

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        context['partner'] = self.object
        message = ''
        if context['action'] == 'created':
            message = 'El socio de negocio ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El socio de negocio ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No es posible eliminar el socio de negocio. Existen dependencias.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'

        context['message'] = message
        return context
