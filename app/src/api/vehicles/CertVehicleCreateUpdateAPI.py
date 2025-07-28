from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import json
from datetime import datetime

from equipment.models.CertificationVehicle import CertificationVehicle
from equipment.models.Vehicle import Vehicle


@method_decorator(csrf_exempt, name='dispatch')
class CertVehicleCreateUpdateAPI(View):
    """
    API para crear y actualizar certificaciones de vehículos.
    """
    
    def post(self, request):
        """Crear una nueva certificación de vehículo"""
        try:
            data = json.loads(request.body)
            return self._create_or_update_certification(data)
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
        """Actualizar una certificación de vehículo existente"""
        try:
            data = json.loads(request.body)
            cert_id = data.get('id')
            
            if not cert_id:
                return JsonResponse({
                    'success': False,
                    'error': 'ID de la certificación es requerido para actualización'
                }, status=400)
            
            return self._create_or_update_certification(data, cert_id)
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
    
    def _create_or_update_certification(self, data, cert_id=None):
        """Método privado para crear o actualizar una certificación"""
        # Validar datos requeridos
        required_fields = ['vehicle_id', 'name', 'date_start', 'date_end']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }, status=400)
        
        try:
            # Validar que el vehículo existe (puede ser None según el modelo)
            vehicle = None
            if data['vehicle_id']:
                vehicle = get_object_or_404(Vehicle, id=data['vehicle_id'])
            
            # Validar formato de fechas
            try:
                date_start = datetime.strptime(data['date_start'], '%Y-%m-%d').date()
                date_end = datetime.strptime(data['date_end'], '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=400)
            
            # Validar que date_end sea posterior a date_start
            if date_end <= date_start:
                return JsonResponse({
                    'success': False,
                    'error': 'La fecha de fin debe ser posterior a la fecha de inicio'
                }, status=400)
            
            # Validar que el nombre de certificación sea válido
            valid_names = [choice[0] for choice in CertificationVehicle.CERTIFICATION_NAME_CHOICES]
            if data['name'] not in valid_names:
                return JsonResponse({
                    'success': False,
                    'error': f'Nombre de certificación inválido. Opciones válidas: {", ".join(valid_names)}'
                }, status=400)
            
            # Crear o actualizar la certificación
            if cert_id:
                # Actualizar certificación existente
                certification = get_object_or_404(CertificationVehicle, id=cert_id)
                certification.vehicle = vehicle
                certification.name = data['name']
                certification.date_start = date_start
                certification.date_end = date_end
                certification.description = data.get('description', '')
                certification.updated_by = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                action = 'actualizada'
            else:
                # Crear nueva certificación
                certification = CertificationVehicle(
                    vehicle=vehicle,
                    name=data['name'],
                    date_start=date_start,
                    date_end=date_end,
                    description=data.get('description', ''),
                    created_by=request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                )
                action = 'creada'
            
            # Guardar en base de datos
            certification.full_clean()  # Validación del modelo
            certification.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Certificación de vehículo {action} exitosamente',
                'data': {
                    'id': certification.id,
                    'vehicle_id': certification.vehicle.id if certification.vehicle else None,
                    'vehicle_plate': certification.vehicle.no_plate if certification.vehicle else None,
                    'name': certification.name,
                    'name_display': certification.get_name_display(),
                    'date_start': certification.date_start.strftime('%Y-%m-%d'),
                    'date_end': certification.date_end.strftime('%Y-%m-%d'),
                    'description': certification.description,
                    'created_at': certification.created_at.isoformat() if certification.created_at else None,
                    'updated_at': certification.updated_at.isoformat() if certification.updated_at else None
                }
            })
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': f'Error de validación: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)
    
    def get(self, request):
        """Obtener certificaciones de vehículos"""
        try:
            vehicle_id = request.GET.get('vehicle_id')
            cert_id = request.GET.get('id')
            
            if cert_id:
                # Obtener una certificación específica
                certification = get_object_or_404(CertificationVehicle, id=cert_id, is_active=True)
                data = {
                    'id': certification.id,
                    'vehicle_id': certification.vehicle.id if certification.vehicle else None,
                    'vehicle_plate': certification.vehicle.no_plate if certification.vehicle else None,
                    'name': certification.name,
                    'name_display': certification.get_name_display(),
                    'date_start': certification.date_start.strftime('%Y-%m-%d'),
                    'date_end': certification.date_end.strftime('%Y-%m-%d'),
                    'description': certification.description,
                    'created_at': certification.created_at.isoformat() if certification.created_at else None,
                    'updated_at': certification.updated_at.isoformat() if certification.updated_at else None
                }
                return JsonResponse({'success': True, 'data': data})
            
            elif vehicle_id:
                # Obtener certificaciones de un vehículo específico
                certifications = CertificationVehicle.objects.filter(
                    vehicle_id=vehicle_id, 
                    is_active=True
                ).select_related('vehicle')
                data = []
                for certification in certifications:
                    data.append({
                        'id': certification.id,
                        'vehicle_id': certification.vehicle.id if certification.vehicle else None,
                        'vehicle_plate': certification.vehicle.no_plate if certification.vehicle else None,
                        'name': certification.name,
                        'name_display': certification.get_name_display(),
                        'date_start': certification.date_start.strftime('%Y-%m-%d'),
                        'date_end': certification.date_end.strftime('%Y-%m-%d'),
                        'description': certification.description,
                        'created_at': certification.created_at.isoformat() if certification.created_at else None,
                        'updated_at': certification.updated_at.isoformat() if certification.updated_at else None
                    })
                return JsonResponse({'success': True, 'data': data})
            
            else:
                # Obtener todas las certificaciones activas
                certifications = CertificationVehicle.objects.filter(is_active=True).select_related('vehicle')
                data = []
                for certification in certifications:
                    data.append({
                        'id': certification.id,
                        'vehicle_id': certification.vehicle.id if certification.vehicle else None,
                        'vehicle_plate': certification.vehicle.no_plate if certification.vehicle else None,
                        'name': certification.name,
                        'name_display': certification.get_name_display(),
                        'date_start': certification.date_start.strftime('%Y-%m-%d'),
                        'date_end': certification.date_end.strftime('%Y-%m-%d'),
                        'description': certification.description,
                        'created_at': certification.created_at.isoformat() if certification.created_at else None,
                        'updated_at': certification.updated_at.isoformat() if certification.updated_at else None
                    })
                return JsonResponse({'success': True, 'data': data})
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)