from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

from equipment.models.PassVehicle import PassVehicle


@method_decorator(csrf_exempt, name='dispatch')
class PassVehicleDeleteAPI(View):
    """
    API para eliminar pases de vehículos (soft delete).
    """
    
    def delete(self, request, pk):
        """Eliminar un pase de vehículo (soft delete)"""
        try:
            # El ID viene del parámetro pk de la URL
            pass_id = pk
            
            # Buscar el pase
            pass_vehicle = get_object_or_404(PassVehicle, id=pass_id, is_active=True)
            
            # Realizar soft delete
            pass_vehicle.is_active = False
            pass_vehicle.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Pase de vehículo eliminado exitosamente',
                'data': {
                    'id': pass_vehicle.id,
                    'vehicle_plate': pass_vehicle.vehicle.no_plate,
                    'bloque': pass_vehicle.bloque
                }
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
    
    def post(self, request):
        """Eliminar múltiples pases de vehículos"""
        try:
            data = json.loads(request.body)
            pass_ids = data.get('ids', [])
            
            if not pass_ids or not isinstance(pass_ids, list):
                return JsonResponse({
                    'success': False,
                    'error': 'Lista de IDs es requerida'
                }, status=400)
            
            deleted_passes = []
            errors = []
            
            for pass_id in pass_ids:
                try:
                    pass_vehicle = get_object_or_404(PassVehicle, id=pass_id, is_active=True)
                    pass_vehicle.is_active = False
                    pass_vehicle.save()
                    
                    deleted_passes.append({
                        'id': pass_vehicle.id,
                        'vehicle_plate': pass_vehicle.vehicle.no_plate,
                        'bloque': pass_vehicle.bloque
                    })
                except Exception as e:
                    errors.append({
                        'id': pass_id,
                        'error': str(e)
                    })
            
            return JsonResponse({
                'success': True,
                'message': f'{len(deleted_passes)} pases eliminados exitosamente',
                'data': {
                    'deleted': deleted_passes,
                    'errors': errors,
                    'total_deleted': len(deleted_passes),
                    'total_errors': len(errors)
                }
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