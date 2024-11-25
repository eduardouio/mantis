from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from projects.forms import ProjectResourceForm
from projects.models import Project
from equipment.models import ResourceItem
import json


class CreateProjectResource(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        project = Project.get_project_by_id(data['id_project'])
        resource_item = ResourceItem.get_by_id(data['resource_item'])

        form = ProjectResourceForm({
            'project': project,
            'resource_item': resource_item,
            'cost': data['cost'],
            'cost_manteinance': data['cost_manteinance'],
            'is_active': data['is_active'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'mantenance_frequency': data['mantenance_frequency'],
            'times_mantenance': data['times_mantenance'],
            'retired_date': data['retired_date'],
            'motive_retired': data['motive_retired']
        })

        if form.is_valid():
            project_resource = form.save(commit=False)
            project_resource.project = project
            project_resource.save()
            return JsonResponse(
                {'status': 'success'}, status=201
            )

        return JsonResponse(
            {'status': 'error', 'errors': form.errors}, status=400
        )


class UpdateProjectResource(LoginRequiredMixin, View):
    model = Project
    template_name = 'forms/project_form.html'
    fields = [
        'partner', 'place', 'contact_name', 'phone_contact', 'start_date',
        'end_date', 'is_active', 'notes'
    ]
    success_url = '/proyectos/'
