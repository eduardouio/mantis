from projects.models.SheetProject import SheetProject
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from django.http import JsonResponse
from django.views import View


class GetAllSheerProjectItemsAPI(View):
    """Retorna información de las hojas de proyecto."""

    def get(self, request, sheet_project_id=None):
        """Obtener información de una hoja de proyecto específica o todas."""
        try:
            if sheet_project_id:
                return self._get_sheet_project_info(sheet_project_id)
            else:
                return self._get_all_sheets_info()
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def _get_custody_chains_data(self, sheet_project):
        """Obtener las cadenas de custodia de una hoja de proyecto."""
        custody_chains = CustodyChain.objects.filter(
            sheet_project=sheet_project, is_active=True
        ).select_related("technical")  # .prefetch_related('chaincustodydetail_set__resource_item')
        # Eliminar el prefetch para evitar la carga excesiva de datos

        chains_data = []
        for chain in custody_chains:
            # Obtener los detalles de cada cadena de custodia
            details = ChainCustodyDetail.objects.filter(
                custody_chain=chain, is_active=True
            ).select_related("resource_item")

            details_data = []
            for detail in details:
                details_data.append(
                    {
                        "detail_id": detail.id,
                        "resource_item_id": detail.resource_item.id,
                        "resource_name": detail.resource_item.name
                        if hasattr(detail.resource_item, "name")
                        else None,
                        "resource_code": detail.resource_item.code
                        if hasattr(detail.resource_item, "code")
                        else None,
                    }
                )

            chains_data.append(
                {
                    "custody_chain_id": chain.id,
                    "consecutive": chain.consecutive,
                    "technical_id": chain.technical.id,
                    "technical_name": f"{chain.technical.first_name} {chain.technical.last_name}",
                    "activity_date": chain.activity_date.isoformat()
                    if chain.activity_date
                    else None,
                    "location": chain.location,
                    "start_time": chain.start_time.isoformat()
                    if chain.start_time
                    else None,
                    "end_time": chain.end_time.isoformat() if chain.end_time else None,
                    "time_duration": float(chain.time_duration) if chain.time_duration else 0,
                    "contact_name": chain.contact_name,
                    "contact_position": chain.contact_position,
                    "total_gallons": chain.total_gallons,
                    "total_barrels": chain.total_barrels,
                    "total_cubic_meters": chain.total_cubic_meters,
                    "detail": chain.detail,
                    "item_unity": chain.item_unity,
                    "quantity": float(chain.quantity),
                    "unit_price": float(chain.unit_price),
                    "total_line": float(chain.total_line),
                    "unit_measurement": chain.unit_measurement,
                    "total_price": float(chain.total_price),
                    "items": details_data,
                }
            )

        return chains_data

    def _get_sheet_project_info(self, sheet_project_id):
        """Obtener información de una hoja de proyecto específica."""
        try:
            sheet_project = SheetProject.objects.get(
                id=sheet_project_id, is_active=True
            )
        except SheetProject.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Hoja de proyecto no encontrada"},
                status=404,
            )

        custody_chains = self._get_custody_chains_data(sheet_project)

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "sheet_id": sheet_project.id,
                    "project_id": sheet_project.project.id,
                    "issue_date": sheet_project.issue_date.isoformat()
                    if sheet_project.issue_date
                    else None,
                    "period_start": sheet_project.period_start.isoformat()
                    if sheet_project.period_start
                    else None,
                    "period_end": sheet_project.period_end.isoformat()
                    if sheet_project.period_end
                    else None,
                    "status": sheet_project.status,
                    "series_code": sheet_project.series_code,
                    "service_type": sheet_project.service_type,
                    "total": float(sheet_project.total),
                    "custody_chains": custody_chains,
                },
            }
        )

    def _get_all_sheets_info(self):
        """Obtener información de todas las hojas de proyecto activas."""
        sheets = SheetProject.objects.filter(is_active=True).select_related(
            "project__partner"
        )

        all_data = []
        for sheet in sheets:
            custody_chains = self._get_custody_chains_data(sheet)

            all_data.append(
                {
                    "sheet_id": sheet.id,
                    "project_id": sheet.project.id,
                    "issue_date": sheet.issue_date.isoformat()
                    if sheet.issue_date
                    else None,
                    "period_start": sheet.period_start.isoformat()
                    if sheet.period_start
                    else None,
                    "period_end": sheet.period_end.isoformat()
                    if sheet.period_end
                    else None,
                    "status": sheet.status,
                    "series_code": sheet.series_code,
                    "service_type": sheet.service_type,
                    "total": float(sheet.total),
                    "custody_chains": custody_chains,
                }
            )

        return JsonResponse({"success": True, "data": all_data})
