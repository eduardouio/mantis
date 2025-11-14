from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from projects.models import Project
from projects.forms import ProjectForm


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'forms/project_form.html'
    form_class = ProjectForm
    success_url = '/proyectos/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Proyecto {}'.format(
            self.object.partner)
        context['title_page'] = 'Actualizar Proyecto {}'.format(
            self.object.partner)
        return context

    def get_success_url(self):
        url = reverse_lazy('project_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'cardinal_point' not in form.fields:
            model_field = Project._meta.get_field('cardinal_point')
            form.fields['cardinal_point'] = forms.ChoiceField(
                label=model_field.verbose_name,
                required=False,
                choices=[('', '---------')] + list(model_field.choices)
            )
        return form
