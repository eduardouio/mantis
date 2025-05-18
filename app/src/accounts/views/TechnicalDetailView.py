from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from accounts.models import Technical
from datetime import date # Asegúrate de importar date

# Función auxiliar para calcular detalles de caducidad
def get_expiry_details(expiry_date):
    if not expiry_date:
        return {"text": "N/A", "class": "text-gray-500"}

    today = date.today()
    delta = expiry_date - today
    days_remaining = delta.days

    if days_remaining < 0:
        return {"text": "Vencido", "class": "text-error font-bold"}
    elif days_remaining == 0:
        return {"text": "Vence Hoy", "class": "text-error font-bold"}
    elif days_remaining <= 30:
        days_str = f"{days_remaining} día{'s' if days_remaining != 1 else ''}"
        return {"text": days_str, "class": "text-error font-semibold"}
    else:
        days_str = f"{days_remaining} día{'s' if days_remaining != 1 else ''}"
        return {"text": days_str, "class": "text-success font-semibold"}

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

        # Calcular detalles de caducidad para cada fecha relevante
        context['license_expiry_details'] = get_expiry_details(technical.license_expiry_date)
        context['defensive_driving_expiry_details'] = get_expiry_details(technical.defensive_driving_certificate_expiry_date)
        context['mae_expiry_details'] = get_expiry_details(technical.mae_certificate_expiry_date)
        context['medical_expiry_details'] = get_expiry_details(technical.medical_certificate_expiry_date)
        context['quest_end_details'] = get_expiry_details(technical.quest_end_date)
        
        return context
