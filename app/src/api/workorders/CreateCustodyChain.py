from django.http import JsonResponse
from django.views import View
from projects.models.CustodyChain import CustodyChain
from projects.models.SheetProject import SheetProject
from accounts.models.Technical import Technical
import json


class CreateCustodyChainAPI(View):
    """Crear una nueva cadena de custodia."""

    def post(self, request):
        """Crear una cadena de custodia asociada a una planilla."""
        try:
            data = json.loads(request.body)
            sheet_project_id = data.get("sheet_project_id")

            try:
                sheet_project = SheetProject.objects.get(
                    id=sheet_project_id, is_active=True
                )
            except SheetProject.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Planilla de proyecto no encontrada"},
                    status=404,
                )

            try:
                technical = Technical.get_by_dni("999999999")
            except Technical.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Técnico no encontrado"}, status=404
                )

            custody_chain = CustodyChain()
            custody_chain.sheet_project = sheet_project
            custody_chain.technical = technical
            custody_chain.consecutive = CustodyChain.get_next_consecutive()
            custody_chain.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": "Cadena de custodia creada exitosamente",
                    "data": {
                        "custody_chain_id": custody_chain.id,
                        "consecutive": custody_chain.consecutive,
                        "sheet_project_id": sheet_project.id,
                        "technical_id": technical.id,
                        "technical_name": f"{technical.first_name} {technical.last_name}",
                    },
                },
                status=201,
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "Datos JSON inválidos"}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
