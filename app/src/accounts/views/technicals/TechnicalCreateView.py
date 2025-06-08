from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from accounts.models import Technical, VaccinationRecord, PassTechnical
from accounts.forms import TechnicalForm
import json


class TechnicalCreateView(LoginRequiredMixin, CreateView):
    model = Technical
    template_name = 'forms/technical_form.html'
    form_class = TechnicalForm
    success_url = reverse_lazy('technical_list')

    def get_success_url(self):
        url = reverse_lazy('technical_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nuevo Técnico'
        context['title_page'] = 'Registrar Nuevo Técnico'
        return context

    @transaction.atomic
    def form_valid(self, form):
        """Guardar el técnico y procesar datos adicionales de vacunas y pases"""
        response = super().form_valid(form)

        # Procesar vacunas desde el request
        vaccinations_data = self.request.POST.get('vaccinations_data')
        if vaccinations_data:
            try:
                vaccinations = json.loads(vaccinations_data)
                self.create_vaccinations(vaccinations)
            except json.JSONDecodeError:
                pass

        # Procesar pases desde el request
        passes_data = self.request.POST.get('passes_data')
        if passes_data:
            try:
                passes = json.loads(passes_data)
                self.create_passes(passes)
            except json.JSONDecodeError:
                pass

        return response

    def create_vaccinations(self, vaccinations_data):
        """Crear registros de vacunación para el técnico"""
        for vaccination_data in vaccinations_data:
            VaccinationRecord.objects.create(
                technical=self.object,
                vaccine_type=vaccination_data.get('vaccine_type'),
                application_date=vaccination_data.get('application_date'),
                dose_number=vaccination_data.get('dose_number') or None,
                batch_number=vaccination_data.get('batch_number') or None,
                next_dose_date=vaccination_data.get('next_dose_date') or None,
                notes=vaccination_data.get('notes') or None,
                is_active=True
            )

    def create_passes(self, passes_data):
        """Crear pases para el técnico"""
        for pass_data in passes_data:
            PassTechnical.objects.create(
                technical=self.object,
                bloque=pass_data.get('bloque'),
                fecha_caducidad=pass_data.get('fecha_caducidad')
            )

    def post(self, request, *args, **kwargs):
        """Manejar requests AJAX para agregar vacunas y pases"""
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'add_vaccination':
                return self.handle_add_vaccination(data)
            elif action == 'add_pass':
                return self.handle_add_pass(data)

        return super().post(request, *args, **kwargs)

    def handle_add_vaccination(self, data):
        """Manejar adición de vacunación vía AJAX"""
        # Por ahora solo retornamos éxito, los datos se procesarán en form_valid
        return JsonResponse({
            'success': True,
            'message': 'Vacunación agregada correctamente'
        })

    def handle_add_pass(self, data):
        """Manejar adición de pase vía AJAX"""
        # Por ahora solo retornamos éxito, los datos se procesarán en form_valid
        return JsonResponse({
            'success': True,
            'message': 'Pase agregado correctamente'
        })
