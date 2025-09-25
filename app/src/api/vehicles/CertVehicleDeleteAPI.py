from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

from equipment.models.CertificationVehicle import CertificationVehicle


@method_decorator(csrf_exempt, name='dispatch')
class CertVehicleDeleteAPI(View):
    """
    API para eliminar certificaciones de vehículos (soft delete).
    """
    
    def delete(self, request):
        """Eliminar una certificación de vehículo (soft delete)"""
        try:
            data = json.loads(request.body)
            cert_id = data.get('id')
            
            if not cert_id:
                return JsonResponse({
                    'success': False,
                    'error': 'ID de la certificación es requerido'
                }, status=400)
            
            # Buscar la certificación
            certification = get_object_or_404(CertificationVehicle, id=cert_id, is_active=True)
            
            # Realizar soft delete
            certification.is_active = False
            certification.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Certificación de vehículo eliminada exitosamente',
                'data': {
                    'id': certification.id,
                    'vehicle_plate': certification.vehicle.no_plate if certification.vehicle else None,
                    'name': certification.name,
                    'name_display': certification.get_name_display()
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
        """Eliminar múltiples certificaciones de vehículos"""
        try:
            data = json.loads(request.body)
            cert_ids = data.get('ids', [])
            
            if not cert_ids or not isinstance(cert_ids, list):
                return JsonResponse({
                    'success': False,
                    'error': 'Lista de IDs es requerida'
                }, status=400)
            
            deleted_certifications = []
            errors = []
            
            for cert_id in cert_ids:
                try:
                    certification = get_object_or_404(CertificationVehicle, id=cert_id, is_active=True)
                    certification.is_active = False
                    certification.save()
                    
                    deleted_certifications.append({
                        'id': certification.id,
                        'vehicle_plate': certification.vehicle.no_plate if certification.vehicle else None,
                        'name': certification.name,
                        'name_display': certification.get_name_display()
                    })
                except Exception as e:
                    errors.append({
                        'id': cert_id,
                        'error': str(e)
                    })
            
            return JsonResponse({
                'success': True,
                'message': f'{len(deleted_certifications)} certificaciones eliminadas exitosamente',
                'data': {
                    'deleted': deleted_certifications,
                    'errors': errors,
                    'total_deleted': len(deleted_certifications),
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