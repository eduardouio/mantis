from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator  # noqa: F401
from django.views.decorators.csrf import csrf_exempt  # noqa: F401
from django.shortcuts import get_object_or_404
import json

from accounts.models.VaccinationRecord import VaccinationRecord


class DeleteVaccineAPI(View):
	"""Soft delete de registros de vacunación (uno o múltiples)."""

	def delete(self, request):
		try:
			data = json.loads(request.body)
			record_id = data.get('id')
			if not record_id:
				return JsonResponse({'success': False, 'error': 'ID requerido'}, status=400)
			record = get_object_or_404(
				VaccinationRecord, id=record_id, is_active=True
			)
			record.is_active = False
			if getattr(request, 'user', None) and request.user.is_authenticated:
				record.updated_by = request.user
			record.save()
			return JsonResponse({
				'success': True,
				'message': 'Registro de vacunacion eliminado',
				'data': {'id': record.id, 'technical_id': record.technical.id}
			})
		except json.JSONDecodeError:
			return JsonResponse({'success': False, 'error': 'JSON invalido'}, status=400)
		except Exception as e:  # pragma: no cover
			return JsonResponse({'success': False, 'error': str(e)}, status=500)

	def post(self, request):
		"""Eliminar múltiples registros (soft)."""
		try:
			data = json.loads(request.body)
			ids = data.get('ids')
			if not ids or not isinstance(ids, list):
				return JsonResponse({'success': False, 'error': 'ids lista requerida'}, status=400)
			deleted = []
			errors = []
			for rid in ids:
				try:
					record = get_object_or_404(
						VaccinationRecord, id=rid, is_active=True
					)
					record.is_active = False
					if getattr(request, 'user', None) and request.user.is_authenticated:
						record.updated_by = request.user
					record.save()
					deleted.append({'id': record.id})
				except Exception as e:  # pragma: no cover
					errors.append({'id': rid, 'error': str(e)})
			return JsonResponse({
				'success': True,
				'message': f'{len(deleted)} eliminados',
				'data': {'deleted': deleted, 'errors': errors}
			})
		except json.JSONDecodeError:
			return JsonResponse({'success': False, 'error': 'JSON invalido'}, status=400)
		except Exception as e:  # pragma: no cover
			return JsonResponse({'success': False, 'error': str(e)}, status=500)
