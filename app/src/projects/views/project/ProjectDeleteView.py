from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project


class ProjectDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        project = Project.objects.get(pk=kwargs['pk'])
        try:
            project.delete()
            url = reverse_lazy('project_list')
            return f'{url}?action=deleted'
        except Exception as e:
            url = reverse_lazy('project_detail', kwargs={'pk': project.pk})
            return f'{url}?action=no_delete'
