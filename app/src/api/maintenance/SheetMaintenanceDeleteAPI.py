from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from projects.models.SheetMaintenance import SheetMaintenance


@method_decorator(csrf_exempt, name='dispatch')
class SheetMaintenanceDeleteAPI(View):
    """API para eliminar (borrado lógico) una hoja de mantenimiento."""

    def delete(self, request, pk):
        """Marca una hoja de mantenimiento como eliminada. Solo hojas en BORRADOR."""
        try:
            sheet = get_object_or_404(
                SheetMaintenance, id=pk, is_deleted=False
            )

            if sheet.status != 'DRAFT':
                return JsonResponse({
                    'success': False,
                    'error': (
                        f'No se puede eliminar una hoja en estado {sheet.get_status_display()}. '
                        'Solo hojas en BORRADOR pueden eliminarse.'
                    )
                }, status=400)

            sheet.is_deleted = True
            sheet.is_active = False
            sheet.save()

            return JsonResponse({
                'success': True,
                'message': f'Hoja de mantenimiento #{sheet.sheet_number} eliminada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
