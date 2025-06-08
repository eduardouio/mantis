from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from equipment.models import Vehicle, CertificationVehicle, PassVehicle
from equipment.forms import VehicleForm
import json


class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    template_name = 'forms/vehicle_form.html'
    form_class = VehicleForm
    success_url = reverse_lazy('equipment:vehicle_list')

    def get_success_url(self):
        url = reverse_lazy('vehicle_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nuevo Vehículo'
        context['title_page'] = 'Registrar Nuevo Vehículo'
        return context

    @transaction.atomic
    def form_valid(self, form):
        """Guardar el vehículo y procesar datos adicionales de certificaciones y pases"""
        response = super().form_valid(form)

        # Procesar certificaciones desde el request
        certifications_data = self.request.POST.get('certifications_data')
        if certifications_data:
            try:
                certifications = json.loads(certifications_data)
                self.create_certifications(certifications)
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

    def create_certifications(self, certifications_data):
        """Crear certificaciones para el vehículo"""
        for certification_data in certifications_data:
            CertificationVehicle.objects.create(
                vehicle=self.object,
                name=certification_data.get('name'),  # Cambiar de certification_type a name
                date_start=certification_data.get('date_start'),  # Cambiar de issue_date
                date_end=certification_data.get('date_end'),  # Cambiar de expiry_date
                description=certification_data.get('description') or None,  # Cambiar de notes
                is_active=True
            )

    def create_passes(self, passes_data):
        """Crear pases para el vehículo"""
        for pass_data in passes_data:
            PassVehicle.objects.create(
                vehicle=self.object,
                bloque=pass_data.get('bloque'),
                fecha_caducidad=pass_data.get('fecha_caducidad')
            )

    def post(self, request, *args, **kwargs):
        """Manejar requests AJAX para agregar certificaciones y pases"""
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'add_certification':
                return self.handle_add_certification(data)
            elif action == 'add_pass':
                return self.handle_add_pass(data)

        # Para requests normales de formulario, continuar con el flujo normal
        self.object = None
        return super().post(request, *args, **kwargs)

    def handle_add_certification(self, data):
        """Manejar adición de certificación vía AJAX"""
        try:
            # Validar campos requeridos
            if not data.get('name') or not data.get('date_start'):  # Cambiar campo
                return JsonResponse({
                    'success': False,
                    'message': 'Tipo de certificación y fecha de inicio son requeridos'
                })

            # Validar formato de fecha
            from datetime import datetime
            try:
                datetime.strptime(data.get('date_start'), '%Y-%m-%d')
                if data.get('date_end'):
                    datetime.strptime(data.get('date_end'), '%Y-%m-%d')
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha inválido'
                })

            return JsonResponse({
                'success': True,
                'message': 'Certificación agregada correctamente',
                'data': {
                    'name': data.get('name'),
                    'date_start': data.get('date_start'),
                    'date_end': data.get('date_end'),
                    'description': data.get('description')
                }
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la certificación: {str(e)}'
            })

    def handle_add_pass(self, data):
        """Manejar adición de pase vía AJAX"""
        try:
            # Validar campos requeridos
            if not data.get('bloque') or not data.get('fecha_caducidad'):
                return JsonResponse({
                    'success': False,
                    'message': 'Bloque y fecha de caducidad son requeridos'
                })

            # Validar formato de fecha
            from datetime import datetime
            try:
                datetime.strptime(data.get('fecha_caducidad'), '%Y-%m-%d')
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha inválido'
                })

            return JsonResponse({
                'success': True,
                'message': 'Pase agregado correctamente',
                'data': {
                    'bloque': data.get('bloque'),
                    'fecha_caducidad': data.get('fecha_caducidad')
                }
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar el pase: {str(e)}'
            })
