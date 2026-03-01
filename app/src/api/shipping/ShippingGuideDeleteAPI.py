from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

from projects.models.ShippingGuide import ShippingGuide


@method_decorator(csrf_exempt, name='dispatch')
class ShippingGuideDeleteAPI(View):
    """API para eliminar (borrado lógico) una guía de remisión."""

    def delete(self, request, pk):
        """Marca una guía de remisión como eliminada."""
        try:
            guide = get_object_or_404(
                ShippingGuide, id=pk, is_deleted=False
            )
            guide.is_deleted = True
            guide.is_active = False
            guide.save()

            return JsonResponse({
                'success': True,
                'message': f'Guía de remisión #{guide.guide_number} eliminada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
