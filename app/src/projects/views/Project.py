import json
from django.http import HttpResponseRedirect, JsonResponse
from decimal import Decimal
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    RedirectView
)
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from projects.models import Project, ProjectResourceItem
from equipment.models import ResourceItem
from projects.forms import ProjectForm


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


class CreateProject(LoginRequiredMixin, CreateView):
    model = ProjectForm
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
    model = ProjectForm
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
        url = '{url}?action=updated'.format(url=url)
        return url


class DeleteProject(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        project = Project.objects.get(pk=kwargs['pk'])
        try:
            project.delete()
            url = reverse_lazy('project_list')
            return '{}?action=deleted'.format(url)
        except Exception as e:
            url = reverse_lazy('project_detail', kwargs={'pk': project.pk})
            return '{}?action=no_delete'.format(url)


class AddEquipmentProject(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        project = Project.get_project_by_id(data['id_project'])
        if project is None:
            return JsonResponse({'message': 'Project not found'}, status=500)

        for item in data['equipments']:
            equipment = ResourceItem.get_by_id(item['id'])
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
