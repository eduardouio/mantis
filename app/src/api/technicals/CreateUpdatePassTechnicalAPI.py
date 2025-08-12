from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator  # noqa: F401
from django.views.decorators.csrf import csrf_exempt  # noqa: F401
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import json
from datetime import datetime

from accounts.models import Technical
from accounts.models.PassTechnical import PassTechnical


class CreateUpdatePassTechnicalAPI(View):
	"""Crear / actualizar / listar pases técnicos."""

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
			pass_id = request.GET.get('id')
			technical_id = request.GET.get('technical_id')
			if pass_id:
				registro = get_object_or_404(
					PassTechnical, id=pass_id, is_active=True
				)
				return JsonResponse({'success': True, 'data': self._serialize(registro)})
			if technical_id:
				qs = PassTechnical.objects.filter(
					technical_id=technical_id, is_active=True
				)
				registros = qs.select_related('technical')
			else:
				registros = PassTechnical.objects.filter(is_active=True).select_related('technical')
			data = [self._serialize(r) for r in registros]
			return JsonResponse({'success': True, 'data': data})
		except Exception as e:  # pragma: no cover
			return JsonResponse({'success': False, 'error': str(e)}, status=500)

	def _create_or_update(self, request, data, pass_id=None):
		required = ['technical_id', 'bloque', 'fecha_caducidad']
		for f in required:
			if not data.get(f):
				return JsonResponse({
					'success': False,
					'error': f'Campo {f} requerido'
				}, status=400)
		try:
			technical = get_object_or_404(Technical, id=data['technical_id'])
			try:
				fecha_cad = datetime.strptime(
					data['fecha_caducidad'], '%Y-%m-%d'
				).date()
			except ValueError:
				return JsonResponse({'success': False, 'error': 'fecha_cad formato'}, status=400)
			valid_bloques = [c[0] for c in PassTechnical.BLOQUE_CHOICES]
			if data['bloque'] not in valid_bloques:
				return JsonResponse({'success': False, 'error': 'bloque invalido'}, status=400)
			if pass_id:
				registro = get_object_or_404(
					PassTechnical, id=pass_id, is_active=True
				)
				registro.technical = technical
				registro.bloque = data['bloque']
				registro.fecha_caducidad = fecha_cad
				if getattr(request, 'user', None) and request.user.is_authenticated:
					registro.updated_by = request.user
				action = 'actualizado'
			else:
				registro = PassTechnical(
					technical=technical,
					bloque=data['bloque'],
					fecha_caducidad=fecha_cad
				)
				if getattr(request, 'user', None) and request.user.is_authenticated:
					registro.created_by = request.user
				action = 'creado'
			registro.full_clean()
			registro.save()
			return JsonResponse({
				'success': True,
				'message': f'Pase {action}',
				'data': self._serialize(registro)
			})
		except ValidationError as e:
			return JsonResponse({'success': False, 'error': str(e)}, status=400)
		except Exception as e:  # pragma: no cover
			return JsonResponse({'success': False, 'error': str(e)}, status=500)

	def _serialize(self, registro):
		return {
			'id': registro.id,
			'technical_id': registro.technical.id,
			'bloque': registro.bloque,
			'fecha_caducidad': registro.fecha_caducidad.strftime('%Y-%m-%d'),
		}
