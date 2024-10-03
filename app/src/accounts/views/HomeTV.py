from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeTV(LoginRequiredMixin, TemplateView):
    template_name = 'base/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context