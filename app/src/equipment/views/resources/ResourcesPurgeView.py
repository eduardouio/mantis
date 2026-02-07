from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from common.CheckAvaliableResources import CheckAvailableResources


class ResourcesPurgeView(LoginRequiredMixin, TemplateView):
    """
    Vista para mostrar el reporte de verificación de equipos.
    """
    template_name = 'reports/purge_equipment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = 'Verificación de Equipos'
        context['show_toolbar'] = False
        context['show_alert'] = False
        
        # Obtener reporte de inconsistencias
        checker = CheckAvailableResources()
        report = checker.check_all_equipments()
        context['report'] = report
        
        return context
