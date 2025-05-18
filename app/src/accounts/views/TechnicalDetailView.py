from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from accounts.models import Technical, PassTechnical, VaccinationRecord # Asegúrate de importar PassTechnical y VaccinationRecord
from datetime import date # Asegúrate de importar date


class DetailTechnical(LoginRequiredMixin, DetailView):
    model = Technical
    template_name = 'presentations/technical_presentation.html'
    context_object_name = 'technical'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = 'Ficha de Técnico'
        context['title_section'] = 'Ficha de Técnico'
        context['action'] = self.request.GET.get('action', None)
        
        technical = self.object

        # Obtener registros de vacunación
        context['vaccination_records'] = VaccinationRecord.objects.filter(technical=technical).order_by('-application_date')

        # Obtener pase técnico
        try:
            context['pass_technical'] = PassTechnical.objects.get(technical=technical)
        except PassTechnical.DoesNotExist:
            context['pass_technical'] = None
        
        return context
