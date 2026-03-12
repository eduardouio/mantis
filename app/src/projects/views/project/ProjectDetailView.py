from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'presentations/project_presentation.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['title_section'] = 'Detalle del Proyecto {}'.format(
            self.object.partner
        )
        context['title_page'] = 'Detalle del Proyecto {}'.format(
            self.object.partner
        )
        context['user_data'] = {
            'id': user.id,
            'username': None,
            'email': user.email,
            'role': getattr(user, 'role', None),
            'siganture_name': getattr(user, 'siganture_name', None),
            'siganture_dni': getattr(user, 'siganture_dni', None),
            'siganture_role': getattr(user, 'siganture_role', None),
        }
        context['popup_window'] = False
        return context
