from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from projects.models import Partner


class PartnerListView(LoginRequiredMixin, ListView):
    model = Partner
    template_name = 'lists/partner_list.html'
    context_object_name = 'partners'
    ordering = ['name']

    def get_queryset(self):
        queryset = Partner.objects.all().order_by('name')

        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(business_tax_id__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(address__icontains=search) |
                Q(name_contact__icontains=search)
            )

        # Filtros específicos
        partner_type = self.request.GET.get('partner_type')
        if partner_type:
            queryset = queryset.filter(partner_type=partner_type)

        address = self.request.GET.get('address')
        if address:
            queryset = queryset.filter(address__icontains=address)

        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'true')

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Socios de Negocio Registrados'
        context['title_page'] = 'Listado de Socios de Negocio'
        
        # Variables para filtros
        context['search'] = self.request.GET.get('search', '')
        context['partner_type'] = self.request.GET.get('partner_type', '')
        context['address'] = self.request.GET.get('address', '')
        context['is_active'] = self.request.GET.get('is_active', '')
        
        # Opciones para los selectores
        try:
            context['partner_type_choices'] = Partner._meta.get_field('partner_type').choices
        except:
            context['partner_type_choices'] = []
        
        context['active_choices'] = [('true', 'Activo'), ('false', 'Inactivo')]
        
        # Obtener direcciones únicas para el filtro (usando address en lugar de city)
        context['address_choices'] = Partner.objects.values_list('address', flat=True).exclude(address__isnull=True).exclude(address__exact='').distinct().order_by('address')

        # Manejo de mensajes de acciones
        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'El socio de negocio ha sido eliminado con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context
