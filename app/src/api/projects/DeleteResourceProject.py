from django.http import HttpResponse
from django.views import View
from projects.models.Project import ProjectResourceItem
from projects.models.CustodyChain import ChainCustodyDetail


class DeleteResourceProjectAPI(View):
    
    def delete(self, request, id_project_resource):
        # Validar que el recurso existe
        try:
            project_resource = ProjectResourceItem.objects.get(id=id_project_resource)
        except ProjectResourceItem.DoesNotExist:
            return HttpResponse(status=404)
        
        custody_chain = ChainCustodyDetail.get_by_resource_id(id_project_resource)
        if custody_chain:
            return HttpResponse(
                "No se puede eliminar el recurso porque ha sido utilizado en una cadena de custodia.",
                status=400
            )
        
        ProjectResourceItem.delete_forever(id_project_resource)
        return HttpResponse(status=204)