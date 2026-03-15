from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
from datetime import datetime

from projects.models.ShippingGuide import ShippingGuide, ShippingGuideDetail
from projects.models.Project import Project
from equipment.models.ResourceItem import ResourceItem


@method_decorator(csrf_exempt, name='dispatch')
class ShippingGuideCreateUpdateAPI(View):
    """API para crear y actualizar guías de remisión."""

    def get(self, request, guide_id=None):
        """Obtener una guía de remisión por ID o listar por proyecto."""
        try:
            if guide_id:
                guide = get_object_or_404(
                    ShippingGuide, id=guide_id, is_deleted=False
                )
                return JsonResponse({
                    'success': True,
                    'data': self._serialize_guide(guide)
                })

            # Listar por proyecto
            project_id = request.GET.get('project_id')
            if not project_id:
                return JsonResponse({
                    'success': False,
                    'error': 'El parámetro project_id es requerido'
                }, status=400)

            guides = ShippingGuide.objects.filter(
                project_id=project_id,
                is_deleted=False
            ).order_by('-guide_number')

            return JsonResponse({
                'success': True,
                'data': [self._serialize_guide(g) for g in guides]
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def post(self, request):
        """Crear una nueva guía de remisión con sus detalles."""
        try:
            data = json.loads(request.body)
            return self._create_guide(data)
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
        """Actualizar una guía de remisión existente."""
        try:
            data = json.loads(request.body)
            guide_id = data.get('id')

            if not guide_id:
                return JsonResponse({
                    'success': False,
                    'error': 'El campo id es requerido para actualización'
                }, status=400)

            return self._update_guide(data, guide_id)
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

    def _create_guide(self, data):
        """Crea una guía de remisión y sus detalles."""
        # Validar campos requeridos
        required_fields = ['project_id', 'issue_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }, status=400)

        # Validar que el proyecto exista
        project = Project.get_by_id(data['project_id'])
        if not project:
            return JsonResponse({
                'success': False,
                'error': 'Proyecto no encontrado'
            }, status=404)

        # Parsear fechas
        issue_date = self._parse_date(data['issue_date'])
        if issue_date is None:
            return JsonResponse({
                'success': False,
                'error': 'Formato de fecha inválido para issue_date. Use YYYY-MM-DD'
            }, status=400)

        start_date = self._parse_date(data.get('start_date'))
        end_date = self._parse_date(data.get('end_date'))

        # Crear la guía (el consecutivo se asigna automáticamente en save)
        guide = ShippingGuide(
            project=project,
            type_shipping_guide=data.get('type_shipping_guide', 'EXIT'),
            issue_date=issue_date,
            start_date=start_date,
            end_date=end_date,
            origin_place=data.get('origin_place'),
            destination_place=data.get('destination_place'),
            carrier_name=data.get('carrier_name'),
            carrier_ci=data.get('carrier_ci'),
            vehicle_plate=data.get('vehicle_plate'),
            dispatcher_name=data.get('dispatcher_name'),
            dispatcher_ci=data.get('dispatcher_ci'),
            contact_name=data.get('contact_name'),
            contact_phone=data.get('contact_phone'),
            recibed_by=data.get('recibed_by'),
            recibed_ci=data.get('recibed_ci'),
            notes=data.get('notes'),
            reason_transport=data.get('reason_transport'),
            cost_transport=data.get('cost_transport', 0),
            sheet_project_logistics_concept=data.get('sheet_project_logistics_concept'),
            cost_stowage=data.get('cost_stowage', 0),
            sheet_project_stowage_concept=data.get('sheet_project_stowage_concept'),
        )

        # Si se proporciona guide_number, validar unicidad
        guide_number = data.get('guide_number')
        if guide_number:
            if ShippingGuide.objects.filter(guide_number=guide_number).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'El número de guía {guide_number} ya existe. Ingrese un número diferente.'
                }, status=400)
            guide.guide_number = guide_number

        guide.save()

        # Crear detalles si se proporcionan
        details = data.get('details', [])
        self._create_details(guide, details)

        return JsonResponse({
            'success': True,
            'message': 'Guía de remisión creada exitosamente',
            'data': self._serialize_guide(guide)
        }, status=201)

    def patch(self, request):
        """Cambiar el estado de una guía de remisión."""
        try:
            data = json.loads(request.body)
            guide_id = data.get('id')
            new_status = data.get('status')

            if not guide_id or not new_status:
                return JsonResponse({
                    'success': False,
                    'error': 'Los campos id y status son requeridos'
                }, status=400)

            guide = ShippingGuide.objects.filter(
                id=guide_id, is_deleted=False
            ).first()

            if not guide:
                return JsonResponse({
                    'success': False,
                    'error': 'Guía de remisión no encontrada'
                }, status=404)

            # Validar transiciones de estado
            valid_transitions = {
                'DRAFT': ['CLOSED', 'VOID'],
                'CLOSED': ['VOID'],
                'VOID': [],
            }

            allowed = valid_transitions.get(guide.status, [])
            if new_status not in allowed:
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede cambiar de {guide.get_status_display()} a {new_status}. '
                             f'Transiciones permitidas: {allowed}'
                }, status=400)

            guide.status = new_status
            guide.save()

            return JsonResponse({
                'success': True,
                'message': f'Estado de la guía actualizado a {guide.get_status_display()}',
                'data': self._serialize_guide(guide)
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

    def _update_guide(self, data, guide_id):
        """Actualiza una guía de remisión existente y sus detalles."""
        guide = ShippingGuide.objects.filter(
            id=guide_id, is_deleted=False
        ).first()

        if not guide:
            return JsonResponse({
                'success': False,
                'error': 'Guía de remisión no encontrada'
            }, status=404)

        # Solo se pueden editar guías en estado BORRADOR
        if guide.status != 'DRAFT':
            return JsonResponse({
                'success': False,
                'error': f'No se puede editar una guía en estado {guide.get_status_display()}. Solo guías en BORRADOR son editables.'
            }, status=400)

        # Actualizar proyecto si se proporciona
        if 'project_id' in data:
            project = Project.get_by_id(data['project_id'])
            if not project:
                return JsonResponse({
                    'success': False,
                    'error': 'Proyecto no encontrado'
                }, status=404)
            guide.project = project

        # Actualizar fechas
        if 'issue_date' in data:
            issue_date = self._parse_date(data['issue_date'])
            if issue_date is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de fecha inválido para issue_date. Use YYYY-MM-DD'
                }, status=400)
            guide.issue_date = issue_date

        if 'start_date' in data:
            guide.start_date = self._parse_date(data['start_date'])

        if 'end_date' in data:
            guide.end_date = self._parse_date(data['end_date'])

        # Actualizar campos de texto opcionales
        optional_fields = [
            'type_shipping_guide', 'origin_place', 'destination_place', 'carrier_name',
            'carrier_ci', 'vehicle_plate', 'dispatcher_name',
            'dispatcher_ci', 'contact_name', 'contact_phone',
            'recibed_by', 'recibed_ci', 'notes', 'reason_transport',
            'sheet_project_logistics_concept', 'sheet_project_stowage_concept',
        ]
        for field in optional_fields:
            if field in data:
                setattr(guide, field, data[field])

        # Campos decimales
        decimal_fields = ['cost_transport', 'cost_stowage']
        for field in decimal_fields:
            if field in data:
                setattr(guide, field, data[field] or 0)

        # Actualizar guide_number si se proporciona, validando unicidad
        if 'guide_number' in data and data['guide_number']:
            new_guide_number = data['guide_number']
            if new_guide_number != guide.guide_number:
                if ShippingGuide.objects.filter(
                    guide_number=new_guide_number
                ).exclude(id=guide.id).exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'El número de guía {new_guide_number} ya existe. Ingrese un número diferente.'
                    }, status=400)
                guide.guide_number = new_guide_number

        guide.save()

        # Actualizar detalles si se proporcionan
        if 'details' in data:
            # Eliminar detalles anteriores y recrear
            ShippingGuideDetail.objects.filter(
                shipping_guide=guide
            ).delete()
            self._create_details(guide, data['details'])

        # Recargar la guía para incluir los detalles actualizados
        guide.refresh_from_db()

        return JsonResponse({
            'success': True,
            'message': 'Guía de remisión actualizada exitosamente',
            'data': self._serialize_guide(guide)
        })

    def _create_details(self, guide, details):
        """Crea los detalles de una guía de remisión."""
        instances = []
        for detail_data in details:
            if not detail_data.get('description') or not detail_data.get('quantity'):
                continue

            # Buscar el recurso si se proporciona id_resource_item
            resource_item = None
            resource_item_id = detail_data.get('id_resource_item')
            if resource_item_id:
                try:
                    resource_item = ResourceItem.objects.get(id=resource_item_id)
                except ResourceItem.DoesNotExist:
                    resource_item = None

            instances.append(ShippingGuideDetail(
                shipping_guide=guide,
                id_resource_item=resource_item,
                description=detail_data['description'],
                quantity=detail_data['quantity'],
                unit=detail_data.get('unit', ''),
            ))

        if instances:
            ShippingGuideDetail.objects.bulk_create(instances)

    def _parse_date(self, date_str):
        """Parsea una cadena de fecha en formato YYYY-MM-DD."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None

    def _serialize_guide(self, guide):
        """Serializa una guía de remisión a diccionario."""
        details = ShippingGuideDetail.objects.filter(
            shipping_guide=guide
        ).select_related('id_resource_item')

        return {
            'id': guide.id,
            'project_id': guide.project_id,
            'project_name': str(guide.project),
            'type_shipping_guide': guide.type_shipping_guide,
            'type_shipping_guide_display': guide.get_type_shipping_guide_display(),
            'guide_number': guide.guide_number,
            'issue_date': guide.issue_date.isoformat() if guide.issue_date else None,
            'start_date': guide.start_date.isoformat() if guide.start_date else None,
            'end_date': guide.end_date.isoformat() if guide.end_date else None,
            'origin_place': guide.get_effective_origin_place(),
            'destination_place': guide.get_effective_destination_place(),
            'carrier_name': guide.carrier_name,
            'carrier_ci': guide.carrier_ci,
            'vehicle_plate': guide.vehicle_plate,
            'dispatcher_name': guide.dispatcher_name,
            'dispatcher_ci': guide.dispatcher_ci,
            'contact_name': guide.contact_name,
            'contact_phone': guide.contact_phone,
            'recibed_by': guide.recibed_by,
            'recibed_ci': guide.recibed_ci,
            'notes': guide.notes,
            'reason_transport': guide.reason_transport,
            'reason_transport_display': guide.get_reason_transport_display() if guide.reason_transport else None,
            'cost_transport': float(guide.cost_transport) if guide.cost_transport else 0,
            'sheet_project_logistics_concept': guide.sheet_project_logistics_concept,
            'cost_stowage': float(guide.cost_stowage) if guide.cost_stowage else 0,
            'sheet_project_stowage_concept': guide.sheet_project_stowage_concept,
            'status': guide.status,
            'status_display': guide.get_status_display(),
            'shipping_guide_file': guide.shipping_guide_file.url if guide.shipping_guide_file else None,
            'created_at': guide.created_at.isoformat() if guide.created_at else None,
            'details': [{
                'id': d.id,
                'id_resource_item': d.id_resource_item_id,
                'resource_item_code': d.id_resource_item.code if d.id_resource_item else None,
                'resource_item_name': d.id_resource_item.name if d.id_resource_item else None,
                'type_equipment': d.id_resource_item.type_equipment if d.id_resource_item else None,
                'type_equipment_display': d.id_resource_item.get_type_equipment_display() if d.id_resource_item and d.id_resource_item.type_equipment else None,
                'description': d.description,
                'quantity': d.quantity,
                'unit': d.unit or '',
            } for d in details],
        }
