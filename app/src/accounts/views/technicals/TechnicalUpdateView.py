from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from accounts.models import Technical, VaccinationRecord, PassTechnical
from accounts.forms.TechnicalForm import TechnicalForm
import json


class TechnicalUpdateView(LoginRequiredMixin, UpdateView):
    model = Technical
    template_name = 'forms/technical_form.html'
    form_class = TechnicalForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Técnico {}'.format(
            self.object.first_name)
        context['title_page'] = 'Actualizar Técnico {}'.format(
            self.object.first_name)

        # Agregar datos existentes de vacunas y pases para el frontend
        # Formatear fechas para campos HTML de tipo date
        vaccinations = VaccinationRecord.objects.filter(
            technical=self.object,
            is_active=True
        ).values(
            'id', 'vaccine_type', 'application_date', 'dose_number',
            'batch_number', 'next_dose_date', 'notes'
        )

        # Convertir fechas a string format YYYY-MM-DD
        for vaccination in vaccinations:
            if vaccination['application_date']:
                vaccination['application_date'] = vaccination[
                    'application_date'].strftime('%Y-%m-%d')
            if vaccination['next_dose_date']:
                vaccination['next_dose_date'] = vaccination[
                    'next_dose_date'].strftime('%Y-%m-%d')

        context['existing_vaccinations'] = list(vaccinations)

        passes = PassTechnical.objects.filter(
            technical=self.object
        ).values('id', 'bloque', 'fecha_caducidad')

        # Convertir fechas a string format YYYY-MM-DD
        for pass_data in passes:
            if pass_data['fecha_caducidad']:
                pass_data['fecha_caducidad'] = pass_data[
                    'fecha_caducidad'].strftime('%Y-%m-%d')

        context['existing_passes'] = list(passes)

        return context

    def get_success_url(self):
        messages.success(
            self.request,
            f'Técnico {self.object.first_name} {self.object.last_name} '
            f'actualizado exitosamente.'
        )
        url = reverse_lazy('technical_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url

    @transaction.atomic
    def form_valid(self, form):
        """Guardar el técnico y procesar datos de vacunas y pases"""
        response = super().form_valid(form)

        # Procesar vacunas desde el request
        vaccinations_data = self.request.POST.get('vaccinations_data')
        if vaccinations_data:
            try:
                vaccinations = json.loads(vaccinations_data)
                self.update_vaccinations(vaccinations)
            except json.JSONDecodeError:
                pass

        # Procesar pases desde el request
        passes_data = self.request.POST.get('passes_data')
        if passes_data:
            try:
                passes = json.loads(passes_data)
                self.update_passes(passes)
            except json.JSONDecodeError:
                pass

        messages.success(
            self.request,
            'Los datos del técnico han sido actualizados correctamente.'
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Ha ocurrido un error al actualizar los datos. '
            'Por favor, revise los campos.'
        )
        return super().form_invalid(form)

    def update_vaccinations(self, vaccinations_data):
        """Actualizar registros de vacunación para el técnico"""
        # Obtener IDs de vacunas que se mantienen
        vaccination_ids_to_keep = []

        for vaccination_data in vaccinations_data:
            vaccination_id = vaccination_data.get('id')

            if vaccination_id:
                # Actualizar vacuna existente
                try:
                    vaccination = VaccinationRecord.objects.get(
                        id=vaccination_id,
                        technical=self.object
                    )
                    vaccination.vaccine_type = vaccination_data.get(
                        'vaccine_type')
                    vaccination.application_date = vaccination_data.get(
                        'application_date')
                    vaccination.dose_number = vaccination_data.get(
                        'dose_number') or None
                    vaccination.batch_number = vaccination_data.get(
                        'batch_number') or None
                    vaccination.next_dose_date = vaccination_data.get(
                        'next_dose_date') or None
                    vaccination.notes = vaccination_data.get('notes') or None
                    vaccination.save()
                    vaccination_ids_to_keep.append(vaccination_id)
                except VaccinationRecord.DoesNotExist:
                    pass
            else:
                # Crear nueva vacuna
                new_vaccination = VaccinationRecord.objects.create(
                    technical=self.object,
                    vaccine_type=vaccination_data.get('vaccine_type'),
                    application_date=vaccination_data.get('application_date'),
                    dose_number=vaccination_data.get('dose_number') or None,
                    batch_number=vaccination_data.get('batch_number') or None,
                    next_dose_date=vaccination_data.get(
                        'next_dose_date') or None,
                    notes=vaccination_data.get('notes') or None,
                    is_active=True
                )
                vaccination_ids_to_keep.append(new_vaccination.id)

        # Marcar como inactivas las vacunas que no están en la lista
        VaccinationRecord.objects.filter(
            technical=self.object,
            is_active=True
        ).exclude(
            id__in=vaccination_ids_to_keep
        ).update(is_active=False)

    def update_passes(self, passes_data):
        """Actualizar pases para el técnico"""
        # Obtener IDs de pases que se mantienen
        pass_ids_to_keep = []

        for pass_data in passes_data:
            pass_id = pass_data.get('id')

            if pass_id:
                # Actualizar pase existente
                try:
                    technical_pass = PassTechnical.objects.get(
                        id=pass_id,
                        technical=self.object
                    )
                    technical_pass.bloque = pass_data.get('bloque')
                    technical_pass.fecha_caducidad = pass_data.get(
                        'fecha_caducidad')
                    technical_pass.save()
                    pass_ids_to_keep.append(pass_id)
                except PassTechnical.DoesNotExist:
                    pass
            else:
                # Crear nuevo pase
                new_pass = PassTechnical.objects.create(
                    technical=self.object,
                    bloque=pass_data.get('bloque'),
                    fecha_caducidad=pass_data.get('fecha_caducidad')
                )
                pass_ids_to_keep.append(new_pass.id)

        # Eliminar pases que no están en la lista
        PassTechnical.objects.filter(
            technical=self.object
        ).exclude(
            id__in=pass_ids_to_keep
        ).delete()

    def post(self, request, *args, **kwargs):
        """Manejar requests AJAX para agregar/editar vacunas y pases"""
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'add_vaccination':
                return self.handle_add_vaccination(data)
            elif action == 'add_pass':
                return self.handle_add_pass(data)
            elif action == 'delete_vaccination':
                return self.handle_delete_vaccination(data)
            elif action == 'delete_pass':
                return self.handle_delete_pass(data)

        # Para requests normales de formulario, continuar con el flujo normal
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def handle_add_vaccination(self, data):
        """Manejar adición de vacunación vía AJAX"""
        try:
            # Validar campos requeridos
            vaccine_type = data.get('vaccine_type')
            application_date = data.get('application_date')
            if not vaccine_type or not application_date:
                return JsonResponse({
                    'success': False,
                    'message': 'Tipo de vacuna y fecha de aplicación '
                               'son requeridos'
                })

            # Validar formato de fecha
            from datetime import datetime
            try:
                datetime.strptime(data.get('application_date'), '%Y-%m-%d')
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha inválido'
                })

            return JsonResponse({
                'success': True,
                'message': 'Vacunación agregada correctamente',
                'data': {
                    'vaccine_type': data.get('vaccine_type'),
                    'application_date': data.get('application_date'),
                    'dose_number': data.get('dose_number'),
                    'batch_number': data.get('batch_number'),
                    'next_dose_date': data.get('next_dose_date'),
                    'notes': data.get('notes')
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar vacunación: {str(e)}'
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
                'message': f'Error al procesar pase: {str(e)}'
            })

    def handle_delete_vaccination(self, data):
        """Manejar eliminación de vacunación vía AJAX"""
        try:
            vaccination_id = data.get('vaccination_id')
            if not vaccination_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de vacunación requerido'
                })

            # Verificar que la vacunación pertenece al técnico
            try:
                vaccination = VaccinationRecord.objects.get(
                    id=vaccination_id,
                    technical=self.get_object()
                )
                vaccination.is_active = False
                vaccination.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Vacunación eliminada correctamente'
                })
            except VaccinationRecord.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Vacunación no encontrada'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar vacunación: {str(e)}'
            })

    def handle_delete_pass(self, data):
        """Manejar eliminación de pase vía AJAX"""
        try:
            pass_id = data.get('pass_id')
            if not pass_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de pase requerido'
                })

            # Verificar que el pase pertenece al técnico
            try:
                technical_pass = PassTechnical.objects.get(
                    id=pass_id,
                    technical=self.get_object()
                )
                technical_pass.delete()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Pase eliminado correctamente'
                })
            except PassTechnical.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Pase no encontrado'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar pase: {str(e)}'
            })
