from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import json
from datetime import datetime

from equipment.models.PassVehicle import PassVehicle
from equipment.models.Vehicle import Vehicle


@method_decorator(csrf_exempt, name='dispatch')
class PassVehicleCreateUpdateAPI(View):
    """
    API para crear y actualizar pases de vehículos.
    """
    
    def post(self, request):
        """Crear un nuevo pase de vehículo"""
        try:
            data = json.loads(request.body)
            return self._create_or_update_pass(data, request=request)
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
        """Actualizar un pase de vehículo existente"""
        try:
            data = json.loads(request.body)
            pass_id = data.get('id')
            
            if not pass_id:
                return JsonResponse({
                    'success': False,
                    'error': 'ID del pase es requerido para actualización'
                }, status=400)
            
            return self._create_or_update_pass(data, pass_id, request)
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
    
    def _create_or_update_pass(self, data, pass_id=None, request=None):
        """Método privado para crear o actualizar un pase"""
        # Validar datos requeridos
        required_fields = ['vehicle_id', 'bloque', 'fecha_caducidad']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }, status=400)
        
        try:
            # Validar que el vehículo existe
            vehicle = get_object_or_404(Vehicle, id=data['vehicle_id'])
            
            # Validar formato de fecha
            try:
                fecha_caducidad = datetime.strptime(data['fecha_caducidad'], '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=400)
            
            # Validar que el bloque sea válido
            valid_bloques = [choice[0] for choice in PassVehicle.BLOQUE_CHOICES]
            if data['bloque'] not in valid_bloques:
                return JsonResponse({
                    'success': False,
                    'error': f'Bloque inválido. Opciones válidas: {", ".join(valid_bloques)}'
                }, status=400)
            
            # Crear o actualizar el pase
            if pass_id:
                # Actualizar pase existente
                pass_vehicle = get_object_or_404(PassVehicle, id=pass_id)
                pass_vehicle.vehicle = vehicle
                pass_vehicle.bloque = data['bloque']
                pass_vehicle.fecha_caducidad = fecha_caducidad

                action = 'actualizado'
            else:
                # Crear nuevo pase
                pass_vehicle = PassVehicle(
                    vehicle=vehicle,
                    bloque=data['bloque'],
                    fecha_caducidad=fecha_caducidad
                )
                action = 'creado'
            
            # Guardar en base de datos
            pass_vehicle.full_clean()  # Validación del modelo
            pass_vehicle.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Pase de vehículo {action} exitosamente',
                'data': {
                    'id': pass_vehicle.id,
                    'vehicle_id': pass_vehicle.vehicle.id,
                    'vehicle_plate': pass_vehicle.vehicle.no_plate,
                    'bloque': pass_vehicle.bloque,
                    'fecha_caducidad': pass_vehicle.fecha_caducidad.strftime('%Y-%m-%d'),
                    'created_at': pass_vehicle.created_at.isoformat() if pass_vehicle.created_at else None,
                    'updated_at': pass_vehicle.updated_at.isoformat() if pass_vehicle.updated_at else None
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
        """Obtener pases de vehículos"""
        try:
            vehicle_id = request.GET.get('vehicle_id')
            pass_id = request.GET.get('id')
            
            if pass_id:
                # Obtener un pase específico
                pass_vehicle = get_object_or_404(PassVehicle, id=pass_id, is_active=True)
                data = {
                    'id': pass_vehicle.id,
                    'vehicle_id': pass_vehicle.vehicle.id,
                    'vehicle_plate': pass_vehicle.vehicle.no_plate,
                    'bloque': pass_vehicle.bloque,
                    'fecha_caducidad': pass_vehicle.fecha_caducidad.strftime('%Y-%m-%d'),
                    'created_at': pass_vehicle.created_at.isoformat() if pass_vehicle.created_at else None,
                    'updated_at': pass_vehicle.updated_at.isoformat() if pass_vehicle.updated_at else None
                }
                return JsonResponse({'success': True, 'data': data})
            
            elif vehicle_id:
                # Obtener pases de un vehículo específico
                passes = PassVehicle.get_by_vehicle(vehicle_id)
                data = []
                for pass_vehicle in passes:
                    data.append({
                        'id': pass_vehicle.id,
                        'vehicle_id': pass_vehicle.vehicle.id,
                        'vehicle_plate': pass_vehicle.vehicle.no_plate,
                        'bloque': pass_vehicle.bloque,
                        'fecha_caducidad': pass_vehicle.fecha_caducidad.strftime('%Y-%m-%d'),
                        'created_at': pass_vehicle.created_at.isoformat() if pass_vehicle.created_at else None,
                        'updated_at': pass_vehicle.updated_at.isoformat() if pass_vehicle.updated_at else None
                    })
                return JsonResponse({'success': True, 'data': data})
            
            else:
                # Obtener todos los pases activos
                passes = PassVehicle.objects.filter(is_active=True).select_related('vehicle')
                data = []
                for pass_vehicle in passes:
                    data.append({
                        'id': pass_vehicle.id,
                        'vehicle_id': pass_vehicle.vehicle.id,
                        'vehicle_plate': pass_vehicle.vehicle.no_plate,
                        'bloque': pass_vehicle.bloque,
                        'fecha_caducidad': pass_vehicle.fecha_caducidad.strftime('%Y-%m-%d'),
                        'created_at': pass_vehicle.created_at.isoformat() if pass_vehicle.created_at else None,
                        'updated_at': pass_vehicle.updated_at.isoformat() if pass_vehicle.updated_at else None
                    })
                return JsonResponse({'success': True, 'data': data})
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)