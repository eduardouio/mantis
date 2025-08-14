from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import models
import json
from datetime import datetime

from equipment.models import ResourceItem


@method_decorator(csrf_exempt, name='dispatch')
class UpdateResourceAPI(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)

        resource_id = data.get('id')
        if not resource_id:
            return JsonResponse({
                'success': False,
                'error': 'El campo id es requerido'
            }, status=400)

        resource = get_object_or_404(ResourceItem, id=resource_id)

        # Actualizar campos dinámicamente según el modelo
        ignored_fields = []
        errors = {}
        checklist_touched = False
        for field_name, value in data.items():
            if field_name == 'id':
                continue
            try:
                model_field = resource._meta.get_field(field_name)
            except FieldDoesNotExist:
                ignored_fields.append(field_name)
                continue

            # Parseo básico por tipo de campo
            try:
                if isinstance(model_field, models.DateField) and value:
                    # Permite 'YYYY-MM-DD'
                    if isinstance(value, str):
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            errors[field_name] = (
                                'Formato de fecha inválido. Use YYYY-MM-DD'
                            )
                            continue
                if isinstance(model_field, models.DateTimeField) and value:
                    # Permite 'YYYY-MM-DD HH:MM:SS' o ISO; fallback a fecha
                    # simple a medianoche
                    if isinstance(value, str):
                        parsed = None
                        for fmt in (
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%d',
                        ):
                            try:
                                parsed = datetime.strptime(value, fmt)
                                break
                            except ValueError:
                                continue
                        if not parsed:
                            errors[field_name] = (
                                'Formato de fecha/hora inválido'
                            )
                            continue
                        value = parsed
                # Marcar si se tocó algún checklist (have_*)
                if field_name.startswith('have_'):
                    checklist_touched = True
                # BooleanField acepta bool directamente desde JSON
                # Otros tipos los deja tal cual; full_clean validará
                setattr(resource, field_name, value)
            except Exception as e:  # pragma: no cover
                errors[field_name] = str(e)

        if errors:
            return JsonResponse({
                'success': False,
                'error': 'Errores de validación en campos',
                'field_errors': errors,
                'ignored_fields': ignored_fields or None,
            }, status=400)

        try:
            # Si se modificó algún checklist, ajustar estado técnico
            if checklist_touched:
                try:
                    boolean_fields = resource.boolean_fields
                    # Solo considerar los booleanos existentes en el modelo
                    values = []
                    for bf in boolean_fields:
                        # Saltar los que no existan realmente
                        try:
                            resource._meta.get_field(bf)
                        except FieldDoesNotExist:
                            continue
                        values.append(bool(getattr(resource, bf)))
                    if values:
                        all_checked = all(values)
                        if (
                            all_checked and
                            resource.stst_status_equipment == 'INCOMPLETO'
                        ):
                            resource.stst_status_equipment = 'FUNCIONANDO'
                        elif (
                            not all_checked and
                            resource.stst_status_equipment != 'INCOMPLETO'
                        ):
                            resource.stst_status_equipment = 'INCOMPLETO'
                except Exception:
                    # No bloquear por cálculo de estado
                    pass
            resource.full_clean()
            resource.save()
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': 'Error de validación del modelo',
                'details': e.message_dict
            }, status=400)
        except Exception as e:  # pragma: no cover
            return JsonResponse(
                {'success': False, 'error': str(e)}, status=500
            )

        return JsonResponse({
            'success': True,
            'message': 'Equipo actualizado correctamente',
            'data': self._serialize(resource),
            'ignored_fields': ignored_fields or None,
        })

    def _serialize(self, resource: ResourceItem):
        """Serialización mínima y segura del recurso actualizado."""
        base = {
            'id': resource.id,
            'name': getattr(resource, 'name', None),
            'code': getattr(resource, 'code', None),
            'type_equipment': getattr(resource, 'type_equipment', None),
            'is_active': getattr(resource, 'is_active', None),
            'stst_status_equipment': getattr(
                resource, 'stst_status_equipment', None
            ),
        }
        # Fechas opcionales
        updated_at = getattr(resource, 'updated_at', None)
        created_at = getattr(resource, 'created_at', None)
        if created_at:
            base['created_at'] = created_at.isoformat()
        if updated_at:
            base['updated_at'] = updated_at.isoformat()

        return base
