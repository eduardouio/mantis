from django.http import JsonResponse
from django.views import View
from projects.models import SheetProject


class GetAllSheetProjectAPI(View):
    """Obtener todas las hojas de trabajo de un proyecto."""

    def get(self, request, project_id):
        """Obtener hojas de trabajo por proyecto."""
        try:
            sheets = SheetProject.objects.filter(
                project_id=project_id,
                is_active=True
            ).select_related('project').order_by('-created_at')

            data = []
            for sheet in sheets:
                data.append({
                    'id': sheet.id,
                    'series_code': sheet.series_code,
                    'status': sheet.status,
                    'issue_date': sheet.issue_date.isoformat() if sheet.issue_date else None,
                    'period_start': sheet.period_start.isoformat() if sheet.period_start else None,
                    'period_end': sheet.period_end.isoformat() if sheet.period_end else None,
                    'service_type': sheet.service_type,
                    'total_gallons': sheet.total_gallons,
                    'total_barrels': sheet.total_barrels,
                    'total_cubic_meters': sheet.total_cubic_meters,
                    'subtotal': float(sheet.subtotal),
                    'tax_amount': float(sheet.tax_amount),
                    'total': float(sheet.total),
                    'contact_reference': sheet.contact_reference,
                    'contact_phone_reference': sheet.contact_phone_reference,
                })

            return JsonResponse({
                'success': True,
                'data': data
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
