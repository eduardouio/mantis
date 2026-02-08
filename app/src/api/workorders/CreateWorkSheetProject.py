from django.http import JsonResponse
from django.views import View
from django.db import transaction
import json
from datetime import datetime

from projects.models import Project, SheetProject


class CreateWorkSheetProjectAPI(View):
    """Crear hojas de trabajo (SheetProject)."""

    def post(self, request):
        """Crear nueva hoja de trabajo."""
        try:
            data = json.loads(request.body)
            return self._create_sheet(request, data)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "JSON inválido"}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    @transaction.atomic
    def _create_sheet(self, request, data):
        """Crear nueva hoja de trabajo."""
        required_fields = ["project_id", "period_start", "service_type"]
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            return JsonResponse(
                {
                    "success": False,
                    "error": f'Campos requeridos: {", ".join(missing_fields)}',
                },
                status=400,
            )

        try:
            project = Project.objects.get(id=data["project_id"], is_active=True)
        except Project.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Proyecto no encontrado"}, status=404
            )

        existing = SheetProject.objects.filter(
            project=project, status="IN_PROGRESS", is_active=True
        ).exists()

        if existing:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Ya existe una hoja de trabajo en progreso para este proyecto",
                },
                status=400,
            )

        period_start = self._parse_date(data.get("period_start"))
        
        if not period_start:
            return JsonResponse(
                {"success": False, "error": "Fecha de inicio de período inválida"},
                status=400,
            )
        
        series_code = SheetProject.get_next_series_code()
        sheet = SheetProject(
            project=project,
            period_start=period_start,
            status="IN_PROGRESS",
            series_code=series_code,
            secuence_year=int(series_code.split("-")[2]),
            secuence_number=int(series_code.split("-")[3]),
            service_type=data.get("service_type"),
            contact_reference=data.get("contact_reference"),
            contact_phone_reference=data.get("contact_phone_reference")
        )

        sheet.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Hoja de trabajo creada exitosamente",
                "data": {
                    "id": sheet.id,
                    "series_code": sheet.series_code,
                    "project_id": project.id,
                    "period_start": sheet.period_start.isoformat(),
                    "status": sheet.status
                },
            },
            status=201
        )

    def _parse_date(self, date_str):
        """Parsear fecha desde string."""
        if not date_str:
            return None
        if isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None
        return date_str
