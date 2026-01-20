from django.shortcuts import render, get_object_or_404
from django.views import View
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail


class CustodyChainDetailView(View):
    """
    Vista para mostrar el detalle de una cadena de custodia
    """
    template_name = 'presentations/custody_chain_presentation.html'

    def get(self, request, pk, *args, **kwargs):
        """
        Renderiza la vista de detalle/presentación de una cadena de custodia
        """
        # Obtener la cadena de custodia con relaciones
        custody_chain = get_object_or_404(
            CustodyChain.objects.select_related(
                'sheet_project',
                'sheet_project__project',
                'sheet_project__project__partner',
                'technical',
                'vehicle'
            ),
            pk=pk,
            is_active=True,
            is_deleted=False
        )
        
        # Obtener los detalles de recursos asociados
        chain_details = ChainCustodyDetail.objects.filter(
            custody_chain=custody_chain,
            is_active=True,
            is_deleted=False
        ).select_related(
            'project_resource',
            'project_resource__resource_item'
        )
        
        context = {
            'title': f'Cadena de Custodia {custody_chain.consecutive}',
            'custody_chain': custody_chain,
            'chain_details': chain_details,
            'project': custody_chain.sheet_project.project,
            'partner': custody_chain.sheet_project.project.partner,
        }
        
        return render(request, self.template_name, context)
