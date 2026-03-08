from django.http import HttpResponse, JsonResponse
from django.views import View

from projects.models.Project import ProjectResourceItem
from common.EquipmentManager import EquipmentManager, EquipmentManagerError


class DeleteResourceProjectAPI(View):

    def delete(self, request, id_project_resource):
        if not ProjectResourceItem.objects.filter(id=id_project_resource).exists():
            return HttpResponse(status=404)

        try:
            EquipmentManager.delete_from_project(id_project_resource)
            return HttpResponse(status=204)
        except EquipmentManagerError as e:
            return JsonResponse({"error": str(e)}, status=400)
