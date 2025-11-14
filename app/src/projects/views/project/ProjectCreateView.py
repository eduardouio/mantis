from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django import forms
from projects.models import Project, Partner
from projects.forms import ProjectForm


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'forms/project_form.html'
    form_class = ProjectForm
    success_url = '/proyectos/'

    def get_initial(self):
        initial = super().get_initial()
        partner_id = self.request.GET.get('partner')
        if partner_id:
            try:
                partner = get_object_or_404(Partner, pk=partner_id)
                initial['partner'] = partner.id
            except (ValueError, Partner.DoesNotExist):
                pass
        return initial

    def get_success_url(self):
        url = reverse_lazy('project_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partner_id = self.request.GET.get('partner')
        
        if partner_id:
            try:
                partner = get_object_or_404(Partner, pk=partner_id)
                context['title_section'] = f'Crear Proyecto para {partner.name}'
                context['title_page'] = f'Crear Proyecto para {partner.name}'
                context['preselected_partner'] = partner
            except (ValueError, Partner.DoesNotExist):
                context['title_section'] = 'Crear Nuevo Proyecto'
                context['title_page'] = 'Crear Nuevo Proyecto'
        else:
            context['title_section'] = 'Crear Nuevo Proyecto'
            context['title_page'] = 'Crear Nuevo Proyecto'
            
        return context

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
