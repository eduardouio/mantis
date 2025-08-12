from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

from accounts.models.PassTechnical import PassTechnical


@method_decorator(csrf_exempt, name='dispatch')
class DeletePassTechnicalAPI(View):
	"""Soft delete de pases técnicos (uno o múltiples)."""

	def delete(self, request):
		try:
			data = json.loads(request.body)
			pass_id = data.get('id')
			if not pass_id:
				return JsonResponse({'success': False, 'error': 'ID requerido'}, status=400)
			registro = get_object_or_404(
				PassTechnical, id=pass_id, is_active=True
			)
			registro.is_active = False
			if getattr(request, 'user', None) and request.user.is_authenticated:
				registro.updated_by = request.user
			registro.save()
			return JsonResponse({
				'success': True,
				'message': 'Pase eliminado',
				'data': {'id': registro.id, 'technical_id': registro.technical.id}
			})
		except json.JSONDecodeError:
			return JsonResponse({'success': False, 'error': 'JSON invalido'}, status=400)
		except Exception as e:  # pragma: no cover
			return JsonResponse({'success': False, 'error': str(e)}, status=500)

	def post(self, request):
		try:
			data = json.loads(request.body)
			ids = data.get('ids')
			if not ids or not isinstance(ids, list):
				return JsonResponse({'success': False, 'error': 'ids lista requerida'}, status=400)
			deleted = []
			errors = []
			for pid in ids:
				try:
					registro = get_object_or_404(
						PassTechnical, id=pid, is_active=True
					)
					registro.is_active = False
					if getattr(request, 'user', None) and request.user.is_authenticated:
						registro.updated_by = request.user
					registro.save()
					deleted.append({'id': registro.id})
				except Exception as e:  # pragma: no cover
					errors.append({'id': pid, 'error': str(e)})
			return JsonResponse({
				'success': True,
				'message': f'{len(deleted)} eliminados',
				'data': {'deleted': deleted, 'errors': errors}
			})
		except json.JSONDecodeError:
			return JsonResponse({'success': False, 'error': 'JSON invalido'}, status=400)
		except Exception as e:  # pragma: no cover
			return JsonResponse({'success': False, 'error': str(e)}, status=500)
