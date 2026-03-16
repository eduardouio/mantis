from django.http import JsonResponse
from django.views import View

from accounts.models.PassTechnical import PassTechnical
from equipment.models.PassVehicle import PassVehicle
from equipment.models.CertificationVehicle import CertificationVehicle


class AutocompleteAPI(View):
    """Retorna valores únicos para campos dinámicos (autocomplete)."""

    SOURCES = {
        'pass_technical_bloque': lambda: PassTechnical.get_unique_bloques(),
        'pass_vehicle_bloque': lambda: PassVehicle.get_unique_bloques(),
        'certification_vehicle_name': lambda: CertificationVehicle.get_unique_names(),
    }

    def get(self, request):
        field = request.GET.get('field', '')
        source_fn = self.SOURCES.get(field)
        if not source_fn:
            return JsonResponse({
                'success': False,
                'error': f'Campo no soportado: {field}'
            }, status=400)
        return JsonResponse({'success': True, 'data': source_fn()})
