from django.http import JsonResponse
from django.views import View
from projects.models.SheetProject import SheetProject
from projects.models.CustodyChain import CustodyChain
from datetime import date, datetime


class AllCustodyChainProjectAPI(View):
    """Retorna todas las cadenas de custodia asociadas a un proyecto."""

    def get(self, request, project_id):
        try:
            # Consultar las sheets del proyecto
            sheets = SheetProject.objects.filter(
                project_id=project_id,
                is_active=True,
                is_deleted=False
            ).values_list('id', flat=True)

            if not sheets:
                return JsonResponse({
                    "success": True,
                    "data": [],
                    "message": "No se encontraron hojas de proyecto para este proyecto."
                })

            # Consultar las cadenas de custodia asociadas a las sheets
            custody_chains = (
                CustodyChain.objects
                .filter(
                    sheet_project_id__in=sheets,
                    is_active=True,
                    is_deleted=False
                )
                .select_related('technical', 'vehicle', 'sheet_project')
                .order_by('-activity_date', '-consecutive')
            )

            def serialize_date(value):
                if isinstance(value, (date, datetime)):
                    return value.isoformat()
                return value

            data = []
            for chain in custody_chains:
                data.append({
                    "id": chain.id,
                    "consecutive": chain.consecutive,
                    "activity_date": serialize_date(chain.activity_date),
                    "location": chain.location,
                    "issue_date": serialize_date(chain.issue_date),
                    "start_time": serialize_date(chain.start_time),
                    "end_time": serialize_date(chain.end_time),
                    "time_duration": float(chain.time_duration) if chain.time_duration is not None else None,
                    "contact_name": chain.contact_name,
                    "dni_contact": chain.dni_contact,
                    "total_gallons": chain.total_gallons,
                    "total_barrels": chain.total_barrels,
                    "total_cubic_meters": chain.total_cubic_meters,
                    "sheet_project_id": chain.sheet_project_id,
                    "technical": {
                        "id": chain.technical.id,
                        "first_name": chain.technical.first_name,
                        "last_name": chain.technical.last_name,
                    } if chain.technical else None,
                    "vehicle": {
                        "id": chain.vehicle.id,
                        "no_plate": chain.vehicle.no_plate,
                        "brand": chain.vehicle.brand,
                        "model": chain.vehicle.model,
                    } if chain.vehicle else None,
                })

            return JsonResponse({
                "success": True,
                "data": data,
                "count": len(data)
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": f"Error al consultar las cadenas de custodia: {str(e)}"
            }, status=500)