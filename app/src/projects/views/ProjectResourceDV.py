import json
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from projects.models import (
    ProjectResourceItem,
    WorkOrderDetail,
)
from equipment.models import ResourceItem


class DeleteProjectResource(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        resoruce_item = ResourceItem.get_by_id(
            data['resourceItem']['id']
        )

        project_resource = ProjectResourceItem.get_by_id(
            data['projectResource']['id']
        )

        if not project_resource:
            return JsonResponse(
                {
                    'status': 'error',
                    'errors': 'El recurso no existe'
                },
                status=400
            )

        work_order = WorkOrderDetail.get_by_project_resource(
            project_resource
        ).count()

        if work_order:
            return JsonResponse(
                {
                    'status': 'error',
                    'errors': 'El equipos tiene ordenes de trabajo asignadas'
                },
                status=400
            )

        try:
            project_resource.delete()
            resoruce_item.status = 'LIBRE'
            resoruce_item.bg_current_project = None
            resoruce_item.bg_current_location = ''
            resoruce_item.bg_date_commitment = None
            resoruce_item.bg_date_free = None
            resoruce_item.save()
            return JsonResponse(
                {'status': 'success'}, status=201
            )   
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'errors': str(e)}, status=400
            )
