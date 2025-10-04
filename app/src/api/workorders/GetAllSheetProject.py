from django.http import JsonResponse
from django.views import View
from django.db.models import Q

from projects.models import SheetProject, SheetProjectDetail


class GetAllSheetProjectAPI(View):
    """Listar todas las hojas de trabajo con filtros."""

    def get(self, request):
        """Obtener listado de hojas de trabajo."""
        try:
            # Filtros
            project_id = request.GET.get('project_id')
            status = request.GET.get('status')
            search = request.GET.get('search', '').strip()
            period_start = request.GET.get('period_start')
            period_end = request.GET.get('period_end')
            include_details = request.GET.get('include_details', 'false').lower() == 'true'

            # Query base
            qs = SheetProject.objects.filter(
                is_active=True
            ).select_related('project', 'project__partner')

            # Filtrar por proyecto
            if project_id:
                qs = qs.filter(project_id=project_id)

            # Filtrar por estado
            if status:
                qs = qs.filter(status=status)

            # Filtrar por rango de fechas
            if period_start:
                qs = qs.filter(period_start__gte=period_start)
            if period_end:
                qs = qs.filter(period_end__lte=period_end)

            # Búsqueda por texto
            if search:
                qs = qs.filter(
                    Q(series_code__icontains=search) |
                    Q(project__partner__name__icontains=search) |
                    Q(project__location__icontains=search) |
                    Q(client_po_reference__icontains=search) |
                    Q(invoice_reference__icontains=search)
                )

            # Ordenar
            qs = qs.order_by('-created_at')

            # Serializar
            sheets = []
            for sheet in qs:
                sheet_data = self._serialize_sheet(sheet)
                
                if include_details:
                    details = SheetProjectDetail.objects.filter(
                        sheet_project=sheet,
                        is_active=True
                    ).select_related('resource_item')
                    sheet_data['details'] = [
                        self._serialize_detail(d) for d in details
                    ]
                
                sheets.append(sheet_data)

            return JsonResponse({
                'success': True,
                'count': len(sheets),
                'data': sheets
            })

        except Exception as e:  # pragma: no cover
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def _serialize_sheet(self, sheet):
        """Serializar hoja de trabajo."""
        return {
            'id': sheet.id,
            'project_id': sheet.project_id,
            'project_name': sheet.project.partner.name,
            'project_location': sheet.project.location or '',
            'issue_date': sheet.issue_date.isoformat() if sheet.issue_date else None,
            'period_start': sheet.period_start.isoformat() if sheet.period_start else None,
            'period_end': sheet.period_end.isoformat() if sheet.period_end else None,
            'status': sheet.status,
            'status_display': sheet.get_status_display(),
            'series_code': sheet.series_code,
            'service_type': sheet.service_type,
            'total_gallons': sheet.total_gallons,
            'total_barrels': sheet.total_barrels,
            'total_cubic_meters': sheet.total_cubic_meters,
            'client_po_reference': sheet.client_po_reference,
            'contact_reference': sheet.contact_reference,
            'contact_phone_reference': sheet.contact_phone_reference,
            'final_disposition_reference': sheet.final_disposition_reference,
            'invoice_reference': sheet.invoice_reference,
            'subtotal': float(sheet.subtotal),
            'tax_amount': float(sheet.tax_amount),
            'total': float(sheet.total),
            'created_at': sheet.created_at.isoformat(),
            'updated_at': sheet.updated_at.isoformat()
        }

    def _serialize_detail(self, detail):
        """Serializar detalle de hoja de trabajo."""
        return {
            'id': detail.id,
            'resource_item_id': detail.resource_item_id,
            'resource_name': detail.resource_item.name,
            'resource_code': detail.resource_item.code,
            'detail': detail.detail,
            'item_unity': detail.item_unity,
            'quantity': float(detail.quantity),
            'unit_price': float(detail.unit_price),
            'total_line': float(detail.total_line),
            'unit_measurement': detail.unit_measurement,
            'total_price': float(detail.total_price)
        }
