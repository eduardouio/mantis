from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from accounts.models import Technical, PassTechnical, VaccinationRecord


class DetailTechnical(LoginRequiredMixin, DetailView):
    model = Technical
    template_name = 'presentations/technical_presentation.html'
    context_object_name = 'technical'

    def get_queryset(self):
        """
        Sobrescribe get_queryset para asegurar que solo se muestren
        técnicos activos, en línea con la lógica de BaseModel.
        """
        # Technical.objects.filter(is_active=True) es conceptualmente
        # similar a lo que Technical().get_all() haría para la clase Technical.
        return Technical.get_all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = 'Ficha de Técnico'
        context['title_section'] = 'Ficha de Técnico'
        context['action'] = self.request.GET.get('action', None)
        
        context['vaccination_records'] = VaccinationRecord.objects.filter(
            technical=self.object
        ).order_by('-application_date')

