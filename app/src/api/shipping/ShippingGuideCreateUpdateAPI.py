from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
from datetime import datetime

from projects.models.ShippingGuide import ShippingGuide, ShippingGuideDetail
from projects.models.Project import Project


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
        )
        guide.save()

        # Crear detalles si se proporcionan
        details = data.get('details', [])
        self._create_details(guide, details)

        return JsonResponse({
            'success': True,
            'message': 'Guía de remisión creada exitosamente',
            'data': self._serialize_guide(guide)
        }, status=201)

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
            'origin_place', 'destination_place', 'carrier_name',
            'carrier_ci', 'vehicle_plate', 'dispatcher_name',
            'dispatcher_ci', 'contact_name', 'contact_phone',
            'recibed_by', 'recibed_ci', 'notes',
        ]
        for field in optional_fields:
            if field in data:
                setattr(guide, field, data[field])

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
            instances.append(ShippingGuideDetail(
                shipping_guide=guide,
                description=detail_data['description'],
                quantity=detail_data['quantity'],
                unit=detail_data.get('unit', 0),
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
        ).values('id', 'description', 'quantity', 'unit')

        return {
            'id': guide.id,
            'project_id': guide.project_id,
            'project_name': str(guide.project),
            'guide_number': guide.guide_number,
            'issue_date': guide.issue_date.isoformat() if guide.issue_date else None,
            'start_date': guide.start_date.isoformat() if guide.start_date else None,
            'end_date': guide.end_date.isoformat() if guide.end_date else None,
            'origin_place': guide.origin_place,
            'destination_place': guide.destination_place,
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
            'shipping_guide_file': guide.shipping_guide_file.url if guide.shipping_guide_file else None,
            'created_at': guide.created_at.isoformat() if guide.created_at else None,
            'details': list(details),
        }
