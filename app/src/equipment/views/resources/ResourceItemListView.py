from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from equipment.models import ResourceItem
from projects.models import Project


class ResourceItemListView(LoginRequiredMixin, ListView):
    model = ResourceItem
    template_name = 'lists/resource_list.html'
    context_object_name = 'equipments'
    ordering = ['name']
    paginate_by = 100  # Limitar resultados iniciales

    def get_queryset(self):
        # Solo equipos activos (soft delete via is_active)
        # Optimización: solo traer campos necesarios para la tabla
        queryset = ResourceItem.get_all().only(
            'id',
            'code',
            'type_equipment',
            'serial_number',
            'capacity_gallons',
            'plant_capacity',
            'stst_status_equipment',
            'stst_current_project_id',
            'stst_release_date',
            'stst_status_disponibility'
        ).order_by('code')  # Ordenar por código es más rápido que por nombre

        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(brand__icontains=search)
                | Q(model__icontains=search)
                | Q(serial_number__icontains=search)
            )

        # Filtros específicos
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(stst_status_equipment=status)

        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado De Equipos Registrados'
        context['title_page'] = 'Listado De Equipos'

        # Crear diccionario de proyectos para acceso rápido
        project_ids = [item.stst_current_project_id for item in context['equipments'] if item.stst_current_project_id]
        if project_ids:
            projects = Project.objects.filter(
                id__in=project_ids, 
                is_deleted=False
            ).select_related('partner').only('id', 'location', 'partner__name')
            projects_dict = {p.id: {'location': p.location, 'partner_name': p.partner.name} for p in projects}
            
            # Agregar el location y partner_name a cada item
            for item in context['equipments']:
                if item.stst_current_project_id:
                    proj_data = projects_dict.get(item.stst_current_project_id)
                    if proj_data:
                        item.project_location = proj_data['location']
                        item.partner_name = proj_data['partner_name']
                    else:
                        item.project_location = None
                        item.partner_name = None

        # Variables para filtros
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['brand'] = self.request.GET.get('brand', '')
        # Compatibilidad: siempre se listan activos
        context['is_active'] = 'true'

        # Opciones para los selectores
        context['status_choices'] = (
            ResourceItem._meta.get_field('stst_status_equipment').choices
        )
        # Compatibilidad: solo opción Activo
        context['active_choices'] = [('true', 'Activo')]

        # Obtener marcas únicas para el filtro
        context['brand_choices'] = (
            ResourceItem.objects.values_list('brand', flat=True)
            .exclude(brand__isnull=True)
            .exclude(brand__exact='')
            .distinct()
            .order_by('brand')
        )

        # Manejo de mensajes de acciones
        if 'action' in self.request.GET:
            message = ''
            if self.request.GET.get('action') == 'deleted':
                message = 'El equipo ha sido eliminado con éxito.'
            context['action'] = self.request.GET.get('action')
            context['message'] = message

        return context
