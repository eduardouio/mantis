from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Q
from accounts.models import Technical


class TechnicalListView(LoginRequiredMixin, ListView):
    model = Technical
    template_name = 'lists/technical_list.html'
    context_object_name = 'technicals'
    ordering = ['first_name']

    def get_queryset(self):
        queryset = Technical.objects.all().order_by('first_name')

        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(nro_phone__icontains=search) |
                Q(dni__icontains=search)
            )

        # Filtros específicos
        work_area = self.request.GET.get('work_area')
        if work_area:
            queryset = queryset.filter(work_area=work_area)

        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'true')

        # Filtros de certificados
        has_license = self.request.GET.get('has_license')
        if has_license == 'true':
            queryset = queryset.filter(license_issue_date__isnull=False)
        elif has_license == 'false':
            queryset = queryset.filter(license_issue_date__isnull=True)

        has_defensive_driving = self.request.GET.get('has_defensive_driving')
        if has_defensive_driving == 'true':
            queryset = queryset.filter(defensive_driving_certificate_issue_date__isnull=False)
        elif has_defensive_driving == 'false':
            queryset = queryset.filter(defensive_driving_certificate_issue_date__isnull=True)

        has_mae_certificate = self.request.GET.get('has_mae_certificate')
        if has_mae_certificate == 'true':
            queryset = queryset.filter(mae_certificate_issue_date__isnull=False)
        elif has_mae_certificate == 'false':
            queryset = queryset.filter(mae_certificate_issue_date__isnull=True)

        has_medical_certificate = self.request.GET.get('has_medical_certificate')
        if has_medical_certificate == 'true':
            queryset = queryset.filter(medical_certificate_issue_date__isnull=False)
        elif has_medical_certificate == 'false':
            queryset = queryset.filter(medical_certificate_issue_date__isnull=True)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Técnicos'
        context['title_page'] = 'Listado de Técnicos'
        
        # Variables para filtros
        context['search'] = self.request.GET.get('search', '')
        context['work_area'] = self.request.GET.get('work_area', '')
        context['is_active'] = self.request.GET.get('is_active', '')
        context['has_license'] = self.request.GET.get('has_license', '')
        context['has_defensive_driving'] = self.request.GET.get('has_defensive_driving', '')
        context['has_mae_certificate'] = self.request.GET.get('has_mae_certificate', '')
        context['has_medical_certificate'] = self.request.GET.get('has_medical_certificate', '')
        
        context['work_area_choices'] = Technical._meta.get_field('work_area').choices
        context['status_choices'] = [('true', 'Activo'), ('false', 'Inactivo')]
        context['certificate_choices'] = [('true', 'Con certificado'), ('false', 'Sin certificado')]

        # Manejo de mensajes de acciones
        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'El técnico ha sido eliminado con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context
