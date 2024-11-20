import json
from django.http import JsonResponse
from projects.models import Project
from equipment.models import ResourceItem, Vehicle
from django.views import View


class ProjectDataView(View):

    def get(self, request, id, *args, **kwargs):
        data = {
            'techincals': [],
            'equipments': [],
            'project': None,
            'workOrders': [],
            'currentUser': None,
        }
        return JsonResponse(data)
