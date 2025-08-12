from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import json
from datetime import datetime

from accounts.models import Technical
from accounts.models.VaccinationRecord import VaccinationRecord


class CreateUpdateVaccineAPI(View):
	"""Crear / actualizar / listar registros de vacunación."""

	def post(self, request):
		try:
			data = json.loads(request.body)
			return self._create_or_update(request, data)
		except json.JSONDecodeError:
			return JsonResponse({'success': False, 'error': 'JSON invalido'}, status=400)
		except Exception as e:  # pragma: no cover
			return JsonResponse({'success': False, 'error': str(e)}, status=500)

	def put(self, request):
		try:
			data = json.loads(request.body)
			if not data.get('id'):
				return JsonResponse({'success': False, 'error': 'ID requerido'}, status=400)
			return self._create_or_update(request, data, data['id'])
		except json.JSONDecodeError:
			return JsonResponse({'success': False, 'error': 'JSON invalido'}, status=400)
		except Exception as e:  # pragma: no cover
			return JsonResponse({'success': False, 'error': str(e)}, status=500)

	def get(self, request):
		try:
			record_id = request.GET.get('id')
			technical_id = request.GET.get('technical_id')
			if record_id:
				record = get_object_or_404(
					VaccinationRecord, id=record_id, is_active=True
				)
				return JsonResponse({'success': True, 'data': self._serialize(record)})
			if technical_id:
				records = VaccinationRecord.get_all_by_technical(technical_id)
			else:
				qs = VaccinationRecord.objects.filter(is_active=True)
				records = qs.select_related('technical')
			data = [self._serialize(r) for r in records]
			return JsonResponse({'success': True, 'data': data})
		except Exception as e:  # pragma: no cover
			return JsonResponse({'success': False, 'error': str(e)}, status=500)

	def _create_or_update(self, request, data, record_id=None):
		required = ['technical_id', 'vaccine_type', 'application_date']
		for f in required:
			if not data.get(f):
				return JsonResponse({
					'success': False,
					'error': f'Campo {f} requerido'
				}, status=400)
		try:  # pragma: no cover
			technical = get_object_or_404(Technical, id=data['technical_id'])
			try:
				application_date = datetime.strptime(
					data['application_date'], '%Y-%m-%d'
				).date()
			except ValueError:
				return JsonResponse({
					'success': False,
					'error': 'application_date formato'
				}, status=400)
			next_dose_date = None
			if data.get('next_dose_date'):
				try:
					next_dose_date = datetime.strptime(
						data['next_dose_date'], '%Y-%m-%d'
					).date()
				except ValueError:
					return JsonResponse({
						'success': False,
						'error': 'next_dose_date formato'
					}, status=400)
			valid_types = [c[0] for c in VaccinationRecord.VACCINE_TYPE_CHOICES]
			if data['vaccine_type'] not in valid_types:
				return JsonResponse({
					'success': False,
					'error': 'Tipo vacuna invalido'
				}, status=400)
			if record_id:
				record = get_object_or_404(
					VaccinationRecord, id=record_id, is_active=True
				)
				record.technical = technical
				record.vaccine_type = data['vaccine_type']
				record.batch_number = data.get('batch_number')
				record.application_date = application_date
				record.dose_number = data.get('dose_number')
				record.next_dose_date = next_dose_date
				record.notes = data.get('notes')
				if getattr(request, 'user', None) and request.user.is_authenticated:
					record.updated_by = request.user
				action = 'actualizado'
			else:
				record = VaccinationRecord(
					technical=technical,
					vaccine_type=data['vaccine_type'],
					batch_number=data.get('batch_number'),
					application_date=application_date,
					dose_number=data.get('dose_number'),
					next_dose_date=next_dose_date,
					notes=data.get('notes')
				)
				if getattr(request, 'user', None) and request.user.is_authenticated:
					record.created_by = request.user
				action = 'creado'
			record.full_clean()
			record.save()
			return JsonResponse({
				'success': True,
				'message': f'Registro de vacunacion {action}',
				'data': self._serialize(record)
			})
		except ValidationError as e:
			return JsonResponse({'success': False, 'error': str(e)}, status=400)
		except Exception as e:  # pragma: no cover
			return JsonResponse({'success': False, 'error': str(e)}, status=500)

	def _serialize(self, record):
		return {
			'id': record.id,
			'technical_id': record.technical.id,
			'vaccine_type': record.vaccine_type,
			'vaccine_type_display': record.get_vaccine_type_display(),
			'batch_number': record.batch_number,
			'application_date': record.application_date.strftime('%Y-%m-%d'),
			'dose_number': record.dose_number,
			'next_dose_date': (
				record.next_dose_date.strftime('%Y-%m-%d')
				if record.next_dose_date else None
			),
			'notes': record.notes,
		}
