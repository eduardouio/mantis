from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from accounts.models import Technical, PassTechnical, VaccinationRecord
from datetime import date


class TechnicalDetail(LoginRequiredMixin, DetailView):
    model = Technical
    template_name = 'presentations/technical_presentation.html'
    context_object_name = 'technical'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = 'Ficha de Técnico'
        context['title_section'] = 'Ficha de Técnico'
        context['action'] = self.request.GET.get('action', None)

        # Obtener registros de vacunación
        context['vaccination_records'] = VaccinationRecord.get_all_by_technical(
            technical_id=self.object.id
        )

        # Obtener todos los pases técnicos asociados al técnico
        context['pass_technical'] = PassTechnical.objects.filter(
            technical=self.object
        )

        # Calcular días restantes para las próximas dosis
        next_doses = {}
        for rec in context['vaccination_records']:
            next_doses[rec.id] = {
                'days_left': (rec.next_dose_date - date.today()).days if rec.next_dose_date else None,
                'is_urgent': (rec.next_dose_date - date.today()).days < 15 if rec.next_dose_date else False
            }
        context['vaccination_next_doses'] = next_doses

        return context
