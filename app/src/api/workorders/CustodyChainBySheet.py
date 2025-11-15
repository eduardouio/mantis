from django.http import JsonResponse
from django.views import View
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.SheetProject import SheetProject


class CustodyChainBySheetAPI(View):
    """Obtener todas las cadenas de custodia de una hoja de trabajo."""

    def get(self, request, sheet_project_id):
        """Obtener lista de cadenas de custodia por ID de sheet project."""
        try:
            # Verificar que existe la hoja de trabajo
            try:
                sheet_project = SheetProject.objects.get(id=sheet_project_id, is_active=True)
            except SheetProject.DoesNotExist:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Hoja de trabajo con ID {sheet_project_id} no encontrada"
                    },
                    status=404
                )

            # Obtener todas las cadenas de custodia de esta hoja
            custody_chains = CustodyChain.objects.filter(
                sheet_project=sheet_project,
                is_active=True
            ).order_by('-activity_date', '-id')

            # Construir respuesta con datos de cada cadena
            chains_data = []
            for chain in custody_chains:
                # Contar recursos asociados
                resources_count = ChainCustodyDetail.objects.filter(
                    custody_chain=chain,
                    is_active=True
                ).count()

                chain_info = {
                    "id": chain.id,
                    "consecutive": chain.consecutive,
                    "activity_date": chain.activity_date.strftime("%Y-%m-%d") if chain.activity_date else None,
                    "issue_date": chain.issue_date.strftime("%Y-%m-%d") if chain.issue_date else None,
                    "location": chain.location,
                    "technical_id": chain.technical.id if chain.technical else None,
                    "technical_name": f"{chain.technical.first_name} {chain.technical.last_name}" if chain.technical else None,
                    "vehicle_id": chain.vehicle.id if chain.vehicle else None,
                    "vehicle_plate": chain.vehicle.no_plate if chain.vehicle else None,
                    "start_time": chain.start_time.strftime("%H:%M") if chain.start_time else None,
                    "end_time": chain.end_time.strftime("%H:%M") if chain.end_time else None,
                    "time_duration": float(chain.time_duration) if chain.time_duration else 0,
                    "contact_name": chain.contact_name,
                    "driver_name": chain.driver_name,
                    "total_gallons": chain.total_gallons,
                    "total_barrels": chain.total_barrels,
                    "total_cubic_meters": chain.total_cubic_meters,
                    "resources_count": resources_count,
                    "notes": chain.notes,
                    "created_at": chain.created_at.strftime("%Y-%m-%d %H:%M:%S") if chain.created_at else None
                }
                chains_data.append(chain_info)

            return JsonResponse(
                {
                    "success": True,
                    "message": f"Se encontraron {len(chains_data)} cadenas de custodia",
                    "data": {
                        "sheet_project_id": sheet_project.id,
                        "sheet_project_code": sheet_project.series_code,
                        "project_id": sheet_project.project.id,
                        "project_name": sheet_project.project.partner.name,
                        "total_chains": len(chains_data),
                        "custody_chains": chains_data
                    }
                },
                status=200
            )

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Error inesperado: {str(e)}"
                },
                status=500
            )