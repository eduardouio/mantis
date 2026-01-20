from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from projects.models.CustodyChain import CustodyChain


class CustodyChainListView(View):
    """
    Vista para listar todas las cadenas de custodia
    """
    template_name = 'lists/custody_chain_list.html'
    paginate_by = 20

    def get(self, request, *args, **kwargs):
        """
        Renderiza la lista de cadenas de custodia con filtros y paginación
        """
        # Obtener parámetros de búsqueda
        search_query = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        
        # Base queryset
        custody_chains = CustodyChain.objects.filter(
            is_active=True,
            is_deleted=False
        ).select_related(
            'sheet_project',
            'sheet_project__project',
            'sheet_project__project__partner',
            'technical',
            'vehicle'
        ).order_by('-activity_date', '-id')
        
        # Aplicar filtro de búsqueda
        if search_query:
            custody_chains = custody_chains.filter(
                Q(consecutive__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(sheet_project__series_code__icontains=search_query) |
                Q(sheet_project__project__partner__name__icontains=search_query) |
                Q(technical__first_name__icontains=search_query) |
                Q(technical__last_name__icontains=search_query) |
                Q(vehicle__no_plate__icontains=search_query)
            )
        
        # Paginación
        paginator = Paginator(custody_chains, self.paginate_by)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context = {
            'title': 'Cadenas de Custodia',
            'custody_chains': page_obj,
            'page_obj': page_obj,
            'search_query': search_query,
            'status_filter': status_filter,
            'total_count': paginator.count,
        }
        
        return render(request, self.template_name, context)
