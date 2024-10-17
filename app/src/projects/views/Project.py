from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    RedirectView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project
from django import forms


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'internal_code', 'partner', 'required_by', 'autorized_by',
            'project_name', 'project_description', 'place', 'contact_name',
            'position_contact', 'phone_contact', 'start_date', 'end_date',
            'is_active', 'type_service', 'notes'
        ]
        widgets = {
            'internal_code': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'partner': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'required_by': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'autorized_by': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'project_description': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'notes': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'place': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'position_contact': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'phone_contact': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'type_service': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ListProject(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'lists/project_list.html'
    context_object_name = 'projects'
    ordering = ['project_name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado De Proyectos Registrados'
        context['title_page'] = 'Listado De Proyectos'

        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'El proyecto ha sido eliminado con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context


class DetailProject(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'presentations/project_presentation.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle del Proyecto {}'.format(
            self.object.internal_code
        )
        context['title_page'] = 'Detalle del Proyecto {}'.format(
            self.object.internal_code
        )
        context['equipment'] = Project.get_equipment(self.object.pk)

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        context['project'] = self.object
        message = ''
        if context['action'] == 'created':
            message = 'El proyecto ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El proyecto ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No es posible eliminar el proyecto. Existen dependencias.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'

        context['message'] = message
        return context


class CreateProject(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'forms/project_form.html'
    form_class = ProjectForm
    success_url = '/proyectos/'

    def get_success_url(self):
        url = reverse_lazy('project_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url


class UpdateProject(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'forms/project_form.html'
    form_class = ProjectForm
    success_url = '/proyectos/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Proyecto {}'.format(self.object.internal_code)
        context['title_page'] = 'Actualizar Proyecto {}'.format(self.object.internal_code)
        return context

    def get_success_url(self):
        url = reverse_lazy('project_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url


class DeleteProject(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        project = Project.objects.get(pk=kwargs['pk'])
        try:
            project.delete()
            url = reverse_lazy('project_list')
            return f'{url}?action=deleted'
        except Exception as e:
            return f'{reverse_lazy("project_detail", kwargs={"pk": kwargs["pk"]})}?action=no_delete'
