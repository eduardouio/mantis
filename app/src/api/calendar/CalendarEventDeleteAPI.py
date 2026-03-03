from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from projects.models.CalendarEvent import CalendarEvent


@method_decorator(csrf_exempt, name='dispatch')
class CalendarEventDeleteAPI(View):
    """API para eliminar (borrado lógico) un evento de calendario."""

    def delete(self, request, pk):
        """Marca un evento como eliminado. Solo eventos SCHEDULED pueden eliminarse."""
        try:
            event = get_object_or_404(
                CalendarEvent, id=pk, is_deleted=False
            )

            if event.status not in ('SCHEDULED', 'CANCELLED'):
                return JsonResponse({
                    'success': False,
                    'error': (
                        f'No se puede eliminar un evento en estado {event.get_status_display()}. '
                        'Solo eventos Programados o Cancelados pueden eliminarse.'
                    )
                }, status=400)

            event.is_deleted = True
            event.is_active = False
            event.save()

            return JsonResponse({
                'success': True,
                'message': f'Evento "{event.title}" eliminado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
