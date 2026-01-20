from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.SheetProject import SheetProject
from projects.models.Project import ProjectResourceItem
from accounts.models.Technical import Technical
from equipment.models.Vehicle import Vehicle


class CustodyChainCreateView(View):
    """
    Vista para crear una nueva Cadena de Custodia
    """
    template_name = 'forms/custody_chain_form.html'

    def get(self, request, *args, **kwargs):
        """
        Renderiza el formulario vacío de cadena de custodia
        """
        context = {
            'title': 'Nueva Cadena de Custodia',
            'action': 'create',
            'consecutive': CustodyChain.get_next_consecutive(),
            'sheet_projects': SheetProject.objects.filter(is_active=True, is_deleted=False),
            'technicals': Technical.objects.filter(is_active=True),
            'vehicles': Vehicle.objects.filter(is_active=True),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Procesa el formulario de creación de cadena de custodia
        TODO: Implementar lógica de guardado
        """
        messages.info(request, 'Funcionalidad en desarrollo')
        return redirect('custody_chain_list')
