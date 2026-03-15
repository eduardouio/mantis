from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
from datetime import datetime

from projects.models.SheetMaintenance import SheetMaintenance
from projects.models.SheetProject import SheetProject
from equipment.models.ResourceItem import ResourceItem
from accounts.models.Technical import Technical


@method_decorator(csrf_exempt, name='dispatch')
class SheetMaintenanceCreateUpdateAPI(View):
    """API para crear y actualizar hojas de mantenimiento."""

    def get(self, request, sheet_id=None):
        """Obtener una hoja de mantenimiento por ID o listar por proyecto."""
        try:
            if sheet_id:
                sheet = get_object_or_404(
                    SheetMaintenance, id=sheet_id, is_deleted=False
                )
                return JsonResponse({
                    'success': True,
                    'data': self._serialize(sheet)
                })

            # Listar por hoja de proyecto (sheet_project)
            sheet_project_id = request.GET.get('sheet_project_id')
            if not sheet_project_id:
                return JsonResponse({
                    'success': False,
                    'error': 'El parámetro sheet_project_id es requerido'
                }, status=400)

            sheets = SheetMaintenance.objects.filter(
                id_sheet_project_id=sheet_project_id,
                is_deleted=False
            ).select_related(
                'id_sheet_project__project__partner',
                'responsible_technical',
                'resource_item',
            ).order_by('-sheet_number')

            return JsonResponse({
                'success': True,
                'data': [self._serialize(s) for s in sheets]
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def post(self, request):
        """Crear una nueva hoja de mantenimiento."""
        try:
            data = json.loads(request.body)
            return self._create(data)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def put(self, request):
        """Actualizar una hoja de mantenimiento existente."""
        try:
            data = json.loads(request.body)
            sheet_id = data.get('id')

            if not sheet_id:
                return JsonResponse({
                    'success': False,
                    'error': 'El campo id es requerido para actualización'
                }, status=400)

            return self._update(data, sheet_id)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def patch(self, request):
        """Cambiar el estado de una hoja de mantenimiento (cerrar / anular)."""
        try:
            data = json.loads(request.body)
            sheet_id = data.get('id')
            new_status = data.get('status')

            if not sheet_id or not new_status:
                return JsonResponse({
                    'success': False,
                    'error': 'Los campos id y status son requeridos'
                }, status=400)

            sheet = SheetMaintenance.objects.filter(
                id=sheet_id, is_deleted=False
            ).first()

            if not sheet:
                return JsonResponse({
                    'success': False,
                    'error': 'Hoja de mantenimiento no encontrada'
                }, status=404)

            valid_transitions = {
                'DRAFT': ['CLOSED', 'VOID'],
                'CLOSED': ['VOID'],
                'VOID': [],
            }

            allowed = valid_transitions.get(sheet.status, [])
            if new_status not in allowed:
                return JsonResponse({
                    'success': False,
                    'error': (
                        f'No se puede cambiar de {sheet.get_status_display()} a {new_status}. '
                        f'Transiciones permitidas: {allowed}'
                    )
                }, status=400)

            sheet.status = new_status
            sheet.save()

            return JsonResponse({
                'success': True,
                'message': f'Estado actualizado a {sheet.get_status_display()}',
                'data': self._serialize(sheet)
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    # ── helpers privados ──────────────────────────────────────────────

    def _create(self, data):
        required_fields = ['id_sheet_project', 'start_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }, status=400)

        try:
            sheet_project = SheetProject.objects.get(pk=data['id_sheet_project'])
        except SheetProject.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Hoja de proyecto no encontrada'
            }, status=404)

        if sheet_project.status != 'IN_PROGRESS':
            return JsonResponse({
                'success': False,
                'error': f'No se pueden crear hojas de mantenimiento en una planilla en estado '
                         f'{sheet_project.get_status_display()}. Solo planillas EN EJECUCIÓN son editables.'
            }, status=400)

        start_date = self._parse_datetime(data['start_date'])
        if start_date is None:
            return JsonResponse({
                'success': False,
                'error': 'Formato de fecha inválido para start_date. Use YYYY-MM-DD o YYYY-MM-DDTHH:MM'
            }, status=400)

        end_date = self._parse_datetime(data.get('end_date'))

        # Técnico responsable (opcional)
        responsible_technical = None
        tech_id = data.get('responsible_technical_id')
        if tech_id:
            try:
                responsible_technical = Technical.objects.get(pk=tech_id)
            except Technical.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Técnico responsable no encontrado'
                }, status=404)

        # Equipo (opcional)
        resource_item = None
        resource_id = data.get('resource_item_id')
        if resource_id:
            try:
                resource_item = ResourceItem.objects.get(pk=resource_id)
            except ResourceItem.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Recurso / equipo no encontrado'
                }, status=404)

        sheet = SheetMaintenance(
            id_sheet_project=sheet_project,
            start_date=start_date,
            end_date=end_date,
            responsible_technical=responsible_technical,
            resource_item=resource_item,
            requested_by=data.get('requested_by'),
            rig=data.get('rig'),
            code=data.get('code'),
            location=data.get('location'),
            maintenance_type=data.get('maintenance_type', 'PREVENTIVO'),
            total_days=data.get('total_days', 0),
            cost_day=data.get('cost_day', 0),
            cost_total=data.get('cost_total', 0),
            sheet_project_maintenance_concept=data.get('sheet_project_maintenance_concept', 'SERVICIO TÉCNICO ESPECIALIZADO'),
            sheet_project_logistics_concept=data.get('sheet_project_logistics_concept'),
            cost_logistics=data.get('cost_logistics', 0),
            maintenance_description=data.get('maintenance_description'),
            fault_description=data.get('fault_description'),
            possible_causes=data.get('possible_causes'),
            replaced_parts=data.get('replaced_parts'),
            observations=data.get('observations'),
            performed_by=data.get('performed_by'),
            performed_by_position=data.get('performed_by_position'),
            approved_by=data.get('approved_by'),
            approved_by_position=data.get('approved_by_position'),
            notes=data.get('notes'),
        )
        sheet.save()

        return JsonResponse({
            'success': True,
            'message': 'Hoja de mantenimiento creada exitosamente',
            'data': self._serialize(sheet)
        }, status=201)

    def _update(self, data, sheet_id):
        sheet = SheetMaintenance.objects.filter(
            id=sheet_id, is_deleted=False
        ).first()

        if not sheet:
            return JsonResponse({
                'success': False,
                'error': 'Hoja de mantenimiento no encontrada'
            }, status=404)

        if sheet.status != 'DRAFT':
            return JsonResponse({
                'success': False,
                'error': (
                    f'No se puede editar una hoja en estado {sheet.get_status_display()}. '
                    'Solo hojas en BORRADOR son editables.'
                )
            }, status=400)

        # Verificar que la planilla asociada esté en progreso
        if sheet.id_sheet_project.status != 'IN_PROGRESS':
            return JsonResponse({
                'success': False,
                'error': f'No se puede editar una hoja de mantenimiento de una planilla en estado '
                         f'{sheet.id_sheet_project.get_status_display()}.'
            }, status=400)

        # Hoja de proyecto
        if 'id_sheet_project' in data:
            try:
                sheet_project = SheetProject.objects.get(pk=data['id_sheet_project'])
            except SheetProject.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Hoja de proyecto no encontrada'
                }, status=404)
            sheet.id_sheet_project = sheet_project

        # Fechas
        if 'start_date' in data:
            start_date = self._parse_datetime(data['start_date'])
            if start_date is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de fecha inválido para start_date'
                }, status=400)
            sheet.start_date = start_date

        if 'end_date' in data:
            sheet.end_date = self._parse_datetime(data['end_date'])

        # Técnico
        if 'responsible_technical_id' in data:
            tech_id = data['responsible_technical_id']
            if tech_id:
                try:
                    sheet.responsible_technical = Technical.objects.get(pk=tech_id)
                except Technical.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Técnico responsable no encontrado'
                    }, status=404)
            else:
                sheet.responsible_technical = None

        # Equipo
        if 'resource_item_id' in data:
            res_id = data['resource_item_id']
            if res_id:
                try:
                    sheet.resource_item = ResourceItem.objects.get(pk=res_id)
                except ResourceItem.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Recurso / equipo no encontrado'
                    }, status=404)
            else:
                sheet.resource_item = None

        # Campos de texto / numéricos opcionales
        text_fields = [
            'requested_by', 'rig', 'code', 'location',
            'maintenance_type', 'maintenance_description',
            'fault_description', 'possible_causes',
            'replaced_parts', 'observations',
            'performed_by', 'performed_by_position',
            'approved_by', 'approved_by_position', 'notes',
            'sheet_project_maintenance_concept',
            'sheet_project_logistics_concept',
        ]
        for field in text_fields:
            if field in data:
                setattr(sheet, field, data[field])

        int_fields = ['total_days']
        for field in int_fields:
            if field in data:
                setattr(sheet, field, data[field] or 0)

        decimal_fields = ['cost_day', 'cost_total', 'cost_logistics']
        for field in decimal_fields:
            if field in data:
                setattr(sheet, field, data[field] or 0)

        sheet.save()

        return JsonResponse({
            'success': True,
            'message': 'Hoja de mantenimiento actualizada exitosamente',
            'data': self._serialize(sheet)
        })

    def _parse_datetime(self, value):
        """Parsea YYYY-MM-DD o YYYY-MM-DDTHH:MM."""
        if not value:
            return None
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d'):
            try:
                return datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                continue
        return None

    def _serialize(self, sheet):
        return {
            'id': sheet.id,
            'id_sheet_project': sheet.id_sheet_project_id,
            'sheet_project_series': getattr(sheet.id_sheet_project, 'series_code', '') if sheet.id_sheet_project else '',
            'sheet_number': sheet.sheet_number,
            'status': sheet.status,
            'status_display': sheet.get_status_display(),
            'responsible_technical_id': sheet.responsible_technical_id,
            'responsible_technical_name': (
                f'{sheet.responsible_technical.first_name} {sheet.responsible_technical.last_name}'.strip()
                if sheet.responsible_technical else None
            ),
            'requested_by': sheet.requested_by,
            'rig': sheet.rig,
            'resource_item_id': sheet.resource_item_id,
            'resource_item_name': sheet.resource_item.name if sheet.resource_item else None,
            'code': sheet.code,
            'location': sheet.location,
            'maintenance_type': sheet.maintenance_type,
            'maintenance_type_display': sheet.get_maintenance_type_display(),
            'start_date': sheet.start_date.isoformat() if sheet.start_date else None,
            'end_date': sheet.end_date.isoformat() if sheet.end_date else None,
            'total_days': sheet.total_days,
            'cost_day': float(sheet.cost_day) if sheet.cost_day else 0,
            'cost_total': float(sheet.cost_total) if sheet.cost_total else 0,
            'sheet_project_maintenance_concept': sheet.sheet_project_maintenance_concept,
            'sheet_project_logistics_concept': sheet.sheet_project_logistics_concept,
            'cost_logistics': float(sheet.cost_logistics) if sheet.cost_logistics else 0,
            'maintenance_description': sheet.maintenance_description,
            'fault_description': sheet.fault_description,
            'possible_causes': sheet.possible_causes,
            'replaced_parts': sheet.replaced_parts,
            'observations': sheet.observations,
            'performed_by': sheet.performed_by,
            'performed_by_position': sheet.performed_by_position,
            'approved_by': sheet.approved_by,
            'approved_by_position': sheet.approved_by_position,
            'maintenance_file': sheet.maintenance_file.url if sheet.maintenance_file else None,
            'notes': sheet.notes,
            'created_at': sheet.created_at.isoformat() if sheet.created_at else None,
        }
