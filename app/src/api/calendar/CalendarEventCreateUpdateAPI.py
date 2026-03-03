from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
from datetime import datetime

from projects.models.CalendarEvent import CalendarEvent, CalendarEventDetail
from projects.models.Project import Project, ProjectResourceItem
from equipment.models.ResourceItem import ResourceItem
from accounts.models.Technical import Technical


@method_decorator(csrf_exempt, name='dispatch')
class CalendarEventCreateUpdateAPI(View):
    """API para crear, actualizar, listar y mover eventos de calendario."""

    def get(self, request, event_id=None):
        """Obtener un evento por ID o listar eventos por proyecto y mes."""
        try:
            if event_id:
                event = CalendarEvent.objects.filter(
                    id=event_id, is_deleted=False
                ).select_related(
                    'project__partner',
                    'responsible_technical'
                ).first()

                if not event:
                    return JsonResponse({
                        'success': False,
                        'error': 'Evento no encontrado'
                    }, status=404)

                return JsonResponse({
                    'success': True,
                    'data': self._serialize(event, include_details=True)
                })

            # Listar por proyecto y mes
            project_id = request.GET.get('project_id')
            if not project_id:
                return JsonResponse({
                    'success': False,
                    'error': 'El parámetro project_id es requerido'
                }, status=400)

            events = CalendarEvent.objects.filter(
                project_id=project_id,
                is_deleted=False
            ).select_related(
                'project__partner',
                'responsible_technical'
            ).order_by('start_date', 'start_time')

            # Filtrar por mes/año si se proporcionan
            month = request.GET.get('month')
            year = request.GET.get('year')
            if month and year:
                try:
                    month = int(month)
                    year = int(year)
                    from calendar import monthrange
                    _, last_day = monthrange(year, month)
                    date_start = datetime(year, month, 1).date()
                    date_end = datetime(year, month, last_day).date()
                    events = events.filter(
                        start_date__lte=date_end,
                    ).exclude(
                        end_date__lt=date_start,
                        end_date__isnull=False
                    )
                except (ValueError, TypeError):
                    pass

            return JsonResponse({
                'success': True,
                'data': [self._serialize(e) for e in events]
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def post(self, request):
        """Crear un nuevo evento de calendario con detalles."""
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

    def put(self, request, event_id=None):
        """Actualizar un evento de calendario existente."""
        try:
            data = json.loads(request.body)
            eid = event_id or data.get('id')

            if not eid:
                return JsonResponse({
                    'success': False,
                    'error': 'El campo id es requerido para actualización'
                }, status=400)

            return self._update(data, eid)
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

    def patch(self, request, event_id=None):
        """Mover un evento (drag-and-drop): actualiza solo fechas."""
        try:
            data = json.loads(request.body)
            eid = event_id or data.get('id')

            if not eid:
                return JsonResponse({
                    'success': False,
                    'error': 'El campo id es requerido'
                }, status=400)

            return self._move(data, eid)
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

    @transaction.atomic
    def _create(self, data):
        required_fields = ['project_id', 'title', 'start_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }, status=400)

        try:
            project = Project.objects.get(pk=data['project_id'])
        except Project.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Proyecto no encontrado'
            }, status=404)

        start_date = self._parse_date(data['start_date'])
        if start_date is None:
            return JsonResponse({
                'success': False,
                'error': 'Formato de fecha inválido para start_date. Use YYYY-MM-DD'
            }, status=400)

        end_date = self._parse_date(data.get('end_date'))

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

        # Validar tipo de evento
        valid_event_types = ['MAINTENANCE', 'INSTALLATION', 'REMOVAL', 'INSPECTION', 'OTHER']
        event_type = data.get('event_type', 'MAINTENANCE')
        if event_type not in valid_event_types:
            return JsonResponse({
                'success': False,
                'error': f'Tipo de evento inválido. Opciones: {valid_event_types}'
            }, status=400)

        # Validar prioridad
        valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
        priority = data.get('priority', 'MEDIUM')
        if priority not in valid_priorities:
            return JsonResponse({
                'success': False,
                'error': f'Prioridad inválida. Opciones: {valid_priorities}'
            }, status=400)

        event = CalendarEvent(
            project=project,
            title=data['title'],
            description=data.get('description'),
            event_type=event_type,
            priority=priority,
            status='SCHEDULED',
            start_date=start_date,
            end_date=end_date,
            start_time=self._parse_time(data.get('start_time')),
            end_time=self._parse_time(data.get('end_time')),
            responsible_technical=responsible_technical,
            color=data.get('color'),
            notes=data.get('notes'),
        )
        event.save()

        # Crear detalles si se proporcionan
        details_data = data.get('details', [])
        for detail_data in details_data:
            self._create_detail(event, detail_data)

        return JsonResponse({
            'success': True,
            'message': 'Evento de calendario creado exitosamente',
            'data': self._serialize(event, include_details=True)
        }, status=201)

    @transaction.atomic
    def _update(self, data, event_id):
        event = CalendarEvent.objects.filter(
            id=event_id, is_deleted=False
        ).first()

        if not event:
            return JsonResponse({
                'success': False,
                'error': 'Evento no encontrado'
            }, status=404)

        # Proyecto
        if 'project_id' in data:
            try:
                event.project = Project.objects.get(pk=data['project_id'])
            except Project.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Proyecto no encontrado'
                }, status=404)

        # Fechas
        if 'start_date' in data:
            start_date = self._parse_date(data['start_date'])
            if start_date is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de fecha inválido para start_date'
                }, status=400)
            event.start_date = start_date

        if 'end_date' in data:
            event.end_date = self._parse_date(data.get('end_date'))

        # Horas
        if 'start_time' in data:
            event.start_time = self._parse_time(data.get('start_time'))
        if 'end_time' in data:
            event.end_time = self._parse_time(data.get('end_time'))

        # Técnico
        if 'responsible_technical_id' in data:
            tech_id = data['responsible_technical_id']
            if tech_id:
                try:
                    event.responsible_technical = Technical.objects.get(pk=tech_id)
                except Technical.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Técnico responsable no encontrado'
                    }, status=404)
            else:
                event.responsible_technical = None

        # Campos de texto
        text_fields = ['title', 'description', 'event_type', 'priority',
                        'status', 'color', 'notes']
        for field in text_fields:
            if field in data:
                setattr(event, field, data[field])

        event.save()

        # Actualizar detalles si se proporcionan
        if 'details' in data:
            # Eliminar detalles existentes (soft delete)
            CalendarEventDetail.objects.filter(
                calendar_event=event, is_deleted=False
            ).update(is_deleted=True, is_active=False)

            # Crear nuevos detalles
            for detail_data in data['details']:
                self._create_detail(event, detail_data)

        return JsonResponse({
            'success': True,
            'message': 'Evento de calendario actualizado exitosamente',
            'data': self._serialize(event, include_details=True)
        })

    def _move(self, data, event_id):
        """Mover un evento: solo actualizar fechas (drag-and-drop)."""
        event = CalendarEvent.objects.filter(
            id=event_id, is_deleted=False
        ).first()

        if not event:
            return JsonResponse({
                'success': False,
                'error': 'Evento no encontrado'
            }, status=404)

        new_start = data.get('start_date')
        if not new_start:
            return JsonResponse({
                'success': False,
                'error': 'El campo start_date es requerido'
            }, status=400)

        new_start_date = self._parse_date(new_start)
        if new_start_date is None:
            return JsonResponse({
                'success': False,
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }, status=400)

        # Si el evento tiene duración, mover end_date proporcionalmente
        if event.end_date:
            duration = (event.end_date - event.start_date).days
            from datetime import timedelta
            event.end_date = new_start_date + timedelta(days=duration)

        event.start_date = new_start_date

        # Actualizar end_date si se proporciona explícitamente
        if 'end_date' in data:
            event.end_date = self._parse_date(data['end_date'])

        event.save()

        return JsonResponse({
            'success': True,
            'message': 'Evento movido exitosamente',
            'data': self._serialize(event)
        })

    def _create_detail(self, event, detail_data):
        """Crear un detalle de evento."""
        resource_id = detail_data.get('resource_item_id')
        if not resource_id:
            return

        try:
            resource_item = ResourceItem.objects.get(pk=resource_id)
        except ResourceItem.DoesNotExist:
            return

        project_resource_item = None
        pri_id = detail_data.get('project_resource_item_id')
        if pri_id:
            try:
                project_resource_item = ProjectResourceItem.objects.get(pk=pri_id)
            except ProjectResourceItem.DoesNotExist:
                pass

        detail = CalendarEventDetail(
            calendar_event=event,
            resource_item=resource_item,
            project_resource_item=project_resource_item,
            description=detail_data.get('description'),
            cost=detail_data.get('cost', 0),
            is_completed=detail_data.get('is_completed', False),
            completed_date=self._parse_date(detail_data.get('completed_date')),
        )
        detail.save()

    def _parse_date(self, value):
        """Parsea YYYY-MM-DD."""
        if not value:
            return None
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None

    def _parse_time(self, value):
        """Parsea HH:MM o HH:MM:SS."""
        if not value:
            return None
        for fmt in ('%H:%M:%S', '%H:%M'):
            try:
                return datetime.strptime(value, fmt).time()
            except (ValueError, TypeError):
                continue
        return None

    def _serialize(self, event, include_details=False):
        data = {
            'id': event.id,
            'project_id': event.project_id,
            'project_name': event.project.partner.name if event.project and event.project.partner else None,
            'title': event.title,
            'description': event.description,
            'event_type': event.event_type,
            'event_type_display': event.get_event_type_display(),
            'priority': event.priority,
            'priority_display': event.get_priority_display(),
            'status': event.status,
            'status_display': event.get_status_display(),
            'start_date': event.start_date.isoformat() if event.start_date else None,
            'end_date': event.end_date.isoformat() if event.end_date else None,
            'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
            'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
            'responsible_technical_id': event.responsible_technical_id,
            'responsible_technical_name': (
                f'{event.responsible_technical.first_name} {event.responsible_technical.last_name}'.strip()
                if event.responsible_technical else None
            ),
            'color': event.color,
            'notes': event.notes,
            'created_at': event.created_at.isoformat() if event.created_at else None,
        }

        if include_details:
            details = CalendarEventDetail.objects.filter(
                calendar_event=event, is_deleted=False
            ).select_related('resource_item', 'project_resource_item')
            data['details'] = [self._serialize_detail(d) for d in details]

        return data

    def _serialize_detail(self, detail):
        return {
            'id': detail.id,
            'resource_item_id': detail.resource_item_id,
            'resource_item_name': detail.resource_item.name if detail.resource_item else None,
            'resource_item_code': detail.resource_item.code if detail.resource_item else None,
            'project_resource_item_id': detail.project_resource_item_id,
            'description': detail.description,
            'cost': float(detail.cost) if detail.cost else 0,
            'is_completed': detail.is_completed,
            'completed_date': detail.completed_date.isoformat() if detail.completed_date else None,
        }
