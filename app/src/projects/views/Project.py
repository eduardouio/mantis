import json
from django.http import HttpResponseRedirect, JsonResponse
from decimal import Decimal
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    RedirectView
)
from django.views import View
from django import forms
from django.core.serializers import serialize
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project, ProjectResourceItem
from equipment.models import ResourceItem


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'partner', 'place', 'contact_name', 'phone_contact', 'start_date',
            'end_date', 'is_active', 'notes'
        ]
        widgets = {
            'partner': forms.Select(
                attrs={'class': 'form-select form-control-sm'}
            ),
            'notes': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'place': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'contact_name': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'phone_contact': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'start_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-sm',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'end_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-sm',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            )
        }


class ListProject(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'lists/project_list.html'
    context_object_name = 'projects'

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
        free_equipment = ResourceItem.get_free_equipment()
        project_equipment = ProjectResourceItem.get_project_equipment(
            self.object
        )
        context['title_section'] = 'Detalle del Proyecto {}'.format(
            self.object.partner
        )
        context['title_page'] = 'Detalle del Proyecto {}'.format(
            self.object.partner
        )
        context['free_equipment'] = serialize('json', free_equipment)
        context['project_resource'] = []
        context['project_json'] = serialize('json', [self.object])
        context['project'] = self.object

        for i in project_equipment:
            context['project_resource'].append({
                'project_resource': serialize('json', [i]),
                'resourse_item':  serialize('json', [i.resource_item])
            })


        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Crear Nuevo Proyecto'
        context['title_page'] = 'Crear Nuevo Proyecto'
        return context


class UpdateProject(LoginRequiredMixin, UpdateView):
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


class DeleteProject(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        project = Project.objects.get(pk=kwargs['pk'])
        try:
            project.delete()
            url = reverse_lazy('project_list')
            return f'{url}?action=deleted'
        except Exception as e:
            url = reverse_lazy('project_detail', kwargs={'pk': project.pk})
            return f'{url}?action=no_delete'


class AddEquipmentProject(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        project = Project.get_project_by_id(data['id_project'])
        if project is None:
            return JsonResponse({'message': 'Project not found'}, status=500)

        for item in data['equipments']:
            equipment = ResourceItem.get_equipment_by_id(item['id'])
            ProjectResourceItem.objects.create(
                project=project,
                equipment=equipment,
                cost_rent=item['cost_rent'],
                cost_manteinance=item['cost_manteinance'],
                mantenance_frequency=item['frecuency_days'],
                start_date=item['start_date'],
                end_date=item['end_date']
            )
            # actualizamos estado equipo
            equipment.status = 'RENTADO'
            equipment.bg_current_project = project.id
            equipment.bg_current_location = project.place
            equipment.bg_date_commitment = item['start_date']
            equipment.bg_date_free = item['end_date']
            equipment.save()

        return JsonResponse(
            {'message': 'Equipos agregados correctamente', 'status': 201},
            status=201)


class RemoveEquipmentProject(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        project_equipment = ProjectResourceItem.get_by_id(
            data['id_equipment_project']
        )
        equipment = project_equipment.equipment
        equipment.status = 'LIBRE'
        equipment.bg_current_project = None
        equipment.bg_current_location = ''
        equipment.bg_date_commitment = None
        equipment.bg_date_free = None
        project_equipment.delete()
        equipment.save()

        return JsonResponse({
            'message': 'Equipos eliminados correctamente',
            'status': 201},
            status=201
        )


class UpdateEquipmentProject(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        project_equipment = ProjectResourceItem.get_by_id(
            data['id_equipment_project']
        )
        project_equipment.cost_rent = Decimal(data['cost_rent'])
        project_equipment.cost_manteinance = Decimal(data['cost_manteinance'])
        project_equipment.mantenance_frequency = data['mantenance_frequency']
        project_equipment.start_date = data['start_date']
        project_equipment.end_date = data['end_date']

        if not data.get('is_active'):
            project_equipment.is_active = data['is_active']
            project_equipment.retired_date = data['retired_date']
            project_equipment.motive_retired = data['motive_retired']

        project_equipment.save()

        return JsonResponse({
            'message': 'Equipos actualizados correctamente',
            'status': 201
        },
            status=201
        )
