from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
import json
from datetime import date

from projects.models import ProjectResourceItem


class DeleteResourceProjectAPI(View):
    """Eliminar recursos de un proyecto.

    Al eliminar un recurso:
        - Solo se puede eliminar si no tiene mantenimientos asociados
        - stst_status_disponibility -> 'DISPONIBLE'
        - stst_current_location -> 'BASE PEISOL'
        - stst_current_project_id -> NULL
        - stst_commitment_date -> NULL
        - stst_release_date -> NULL
    """

    def delete(self, request):
        """Eliminar recurso del proyecto."""
        try:
            data = json.loads(request.body)
            return self._delete_resource(request, data)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:  # pragma: no cover
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def get(self, request):
        """Obtener información de un recurso en proyecto."""
        try:
            project_resource_id = request.GET.get('project_resource_id')

            if not project_resource_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Debe proporcionar project_resource_id'
                }, status=400)

            project_resource = get_object_or_404(
                ProjectResourceItem,
                id=project_resource_id,
                is_active=True
            )

            return JsonResponse({
                'success': True,
                'data': self._serialize(project_resource)
            })
        except Exception as e:  # pragma: no cover
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    @transaction.atomic
    def _delete_resource(self, request, data):
        """Eliminar recurso de un proyecto si no tiene mantenimientos."""
        if 'project_resource_id' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Campo project_resource_id requerido'
            }, status=400)

        try:
            # Obtener el registro ProjectResourceItem
            project_resource = get_object_or_404(
                ProjectResourceItem,
                id=data['project_resource_id'],
                is_active=True,
                is_retired=False
            )

            resource = project_resource.resource_item

            # TODO: Verificar que no tenga mantenimientos
            # Esta validación se implementará cuando exista
            # el modelo de mantenimientos
            # Por ahora, permitimos la eliminación

            # Actualizar campos del ResourceItem
            resource.stst_status_disponibility = 'DISPONIBLE'
            resource.stst_current_location = 'BASE PEISOL'
            resource.stst_current_project_id = None
            resource.stst_commitment_date = None
            resource.stst_release_date = None

            if (getattr(request, 'user', None) and
                    request.user.is_authenticated):
                resource.updated_by = request.user
                project_resource.updated_by = request.user

            # Marcar como retirado
            project_resource.is_retired = True
            project_resource.retirement_date = date.today()
            project_resource.retirement_reason = data.get(
                'retirement_reason',
                'Liberado del proyecto'
            )

            # Validar y guardar
            resource.full_clean()
            project_resource.full_clean()

            resource.save()
            project_resource.save()

            return JsonResponse({
                'success': True,
                'message': f'Recurso {resource.code} liberado del proyecto',
                'data': {
                    'resource_code': resource.code,
                    'resource_id': resource.id,
                    'status': resource.stst_status_disponibility,
                    'location': resource.stst_current_location
                }
            })

        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except Exception as e:  # pragma: no cover
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def _serialize(self, project_resource):
        """Serializar ProjectResourceItem a JSON."""
        return {
            'id': project_resource.id,
            'project_id': project_resource.project.id,
            'project_name': str(project_resource.project.partner.name),
            'resource_id': project_resource.resource_item.id,
            'resource_code': project_resource.resource_item.code,
            'resource_name': project_resource.resource_item.name,
            'rent_cost': str(project_resource.rent_cost),
            'maintenance_cost': str(project_resource.maintenance_cost),
            'maintenance_interval_days': (
                project_resource.maintenance_interval_days
            ),
            'operation_start_date': (
                project_resource.operation_start_date.strftime('%Y-%m-%d')
            ),
            'operation_end_date': (
                project_resource.operation_end_date.strftime('%Y-%m-%d')
                if project_resource.operation_end_date else None
            ),
            'is_retired': project_resource.is_retired,
            'retirement_date': (
                project_resource.retirement_date.strftime('%Y-%m-%d')
                if project_resource.retirement_date else None
            ),
            'retirement_reason': project_resource.retirement_reason
        }
