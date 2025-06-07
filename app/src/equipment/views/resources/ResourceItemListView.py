from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from equipment.models import ResourceItem


class ResourceItemListView(LoginRequiredMixin, ListView):
    model = ResourceItem
    template_name = 'lists/resource_list.html'
    context_object_name = 'equipments'
    ordering = ['name']

    def get_queryset(self):
        queryset = ResourceItem.objects.all().order_by('name')

        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search) |
                Q(serial_number__icontains=search)
            )

        # Filtros específicos
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'true')

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado De Equipos Registrados'
        context['title_page'] = 'Listado De Equipos'
        
        # Variables para filtros
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['brand'] = self.request.GET.get('brand', '')
        context['is_active'] = self.request.GET.get('is_active', '')
        
        # Opciones para los selectores
        context['status_choices'] = ResourceItem._meta.get_field('status').choices
        context['active_choices'] = [('true', 'Activo'), ('false', 'Inactivo')]
        
        # Obtener marcas únicas para el filtro
        context['brand_choices'] = ResourceItem.objects.values_list('brand', flat=True).distinct().order_by('brand')

        # Manejo de mensajes de acciones
        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'El equipo ha sido eliminado con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context
