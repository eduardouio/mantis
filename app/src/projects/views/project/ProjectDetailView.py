from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project
import json


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'presentations/project_presentation.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle del Proyecto {}'.format(
            self.object.partner
        )
        context['title_page'] = 'Detalle del Proyecto {}'.format(
            self.object.partner
        )
        return context
