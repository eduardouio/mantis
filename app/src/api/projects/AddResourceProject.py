from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
import json
from datetime import datetime, date

from projects.models import Project, ProjectResourceItem
from equipment.models import ResourceItem


class AddResourceProjectAPI(View):
    """API para agregar recursos a un proyecto."""

    def post(self, request):
        """Agregar un recurso al proyecto."""
        try:
            data = json.loads(request.body)
            return self._add_resource(request, data)
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
        """Listar recursos de un proyecto."""
        try:
            project_id = request.GET.get('project_id')
            resource_id = request.GET.get('resource_id')

            if project_id:
                qs = ProjectResourceItem.objects.filter(
                    project_id=project_id,
                    is_active=True,
                    is_retired=False
                ).select_related('project', 'resource_item')
                data = [self._serialize(r) for r in qs]
                return JsonResponse({'success': True, 'data': data})

            if resource_id:
                qs = ProjectResourceItem.objects.filter(
                    resource_item_id=resource_id,
                    is_active=True,
                    is_retired=False
                ).select_related('project', 'resource_item')
                data = [self._serialize(r) for r in qs]
                return JsonResponse({'success': True, 'data': data})

            return JsonResponse({
                'success': False,
                'error': 'Debe proporcionar project_id o resource_id'
            }, status=400)
        except Exception as e:  # pragma: no cover
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    @transaction.atomic
    def _add_resource(self, request, data):
        """Agregar recurso a un proyecto y actualizar campos de estado."""
        required = [
            'project_id',
            'resource_item_id',
            'rent_cost',
            'maintenance_cost',
            'operation_start_date'
        ]
        for f in required:
            if f not in data or data[f] in [None, '']:
                return JsonResponse({
                    'success': False,
                    'error': f'Campo {f} requerido'
                }, status=400)

        try:
            # Obtener proyecto y recurso
            project = get_object_or_404(
                Project,
                id=data['project_id'],
                is_active=True
            )
            resource = get_object_or_404(
                ResourceItem,
                id=data['resource_item_id'],
                is_active=True
            )

            # Verificar que el recurso esté disponible
            if resource.stst_status_disponibility == 'RENTADO':
                return JsonResponse({
                    'success': False,
                    'error': f'El recurso {resource.code} ya está rentado'
                }, status=400)

            # Validar fechas
            try:
                operation_start = datetime.strptime(
                    data['operation_start_date'], '%Y-%m-%d'
                ).date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'operation_start_date inválido (YYYY-MM-DD)'
                }, status=400)

            operation_end = None
            if data.get('operation_end_date'):
                try:
                    operation_end = datetime.strptime(
                        data['operation_end_date'], '%Y-%m-%d'
                    ).date()
                    if operation_end < operation_start:
                        return JsonResponse({
                            'success': False,
                            'error': 'operation_end_date no puede ser '
                                     'anterior a operation_start_date'
                        }, status=400)
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'operation_end_date inválido (YYYY-MM-DD)'
                    }, status=400)

            # Crear registro ProjectResourceItem
            project_resource = ProjectResourceItem(
                project=project,
                resource_item=resource,
                rent_cost=data['rent_cost'],
                maintenance_cost=data['maintenance_cost'],
                maintenance_interval_days=data.get(
                    'maintenance_interval_days', 1
                ),
                operation_start_date=operation_start,
                operation_end_date=(
                    operation_end if operation_end else project.end_date
                )
            )

            if (getattr(request, 'user', None) and
                    request.user.is_authenticated):
                project_resource.created_by = request.user

            # Actualizar campos del ResourceItem
            resource.stst_status_disponibility = 'RENTADO'
            resource.stst_current_location = (
                project.location or f'Proyecto {project.partner.name}'
            )
            resource.stst_current_project_id = project.id

            # Fecha de compromiso: si operation_start es futuro,
            # usar esa; sino, hoy
            today = date.today()
            if operation_start > today:
                resource.stst_commitment_date = operation_start
            else:
                resource.stst_commitment_date = today

            # Fecha de liberación
            resource.stst_release_date = (
                operation_end if operation_end else project.end_date
            )

            if (getattr(request, 'user', None) and
                    request.user.is_authenticated):
                resource.updated_by = request.user

            # Validar y guardar
            project_resource.full_clean()
            resource.full_clean()

            project_resource.save()
            resource.save()

            return JsonResponse({
                'success': True,
                'message': f'Recurso {resource.code} agregado al proyecto',
                'data': self._serialize(project_resource)
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
