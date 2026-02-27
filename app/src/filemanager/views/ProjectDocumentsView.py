from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models.Project import Project


class ProjectDocumentsView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'filemanager/project_documents.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context['title_page'] = f'Documentos - {project.partner.name if project.partner else "Proyecto"}'
        context['project_id'] = project.pk
        context['project_name'] = project.partner.name if project.partner else f'Proyecto #{project.pk}'
        return context
