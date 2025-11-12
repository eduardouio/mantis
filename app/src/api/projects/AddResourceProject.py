from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
import json
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from projects.models import Project, ProjectResourceItem
from equipment.models import ResourceItem


class AddResourceProjectAPI(View):
    """API para agregar recursos a un proyecto."""

    def post(self, request):
        """Agregar un recurso al proyecto."""
        try:
            data = json.loads(request.body)
            return self._add_resource(request, data)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "JSON inválido"}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def get(self, request):
        """Listar recursos de un proyecto."""
        try:
            project_id = request.GET.get("project_id")
            resource_id = request.GET.get("resource_id")

            if project_id:
                qs = ProjectResourceItem.objects.filter(
                    project_id=project_id, is_active=True, is_retired=False
                ).select_related("project", "resource_item")
                data = [self._serialize(r) for r in qs]
                return JsonResponse({"success": True, "data": data})

            if resource_id:
                qs = ProjectResourceItem.objects.filter(
                    resource_item_id=resource_id, is_active=True, is_retired=False
                ).select_related("project", "resource_item")
                data = [self._serialize(r) for r in qs]

                return JsonResponse({"success": True, "data": data}, status=201)

            return JsonResponse(
                {
                    "success": False,
                    "error": "Debe proporcionar project_id o resource_id",
                },
                status=400,
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    @transaction.atomic
    def _add_resource(self, request, data):
        """Agregar recurso a un proyecto y actualizar campos de estado."""
        # Extraer resource_id directamente si viene en el objeto
        resource_id = data.get('resource_id')
        
        # Si no está, intentar extraerlo de la estructura de resource
        if not resource_id:
            resource_raw = data.get("resource")
            if isinstance(resource_raw, dict):
                # Manejar estructura de Vue con _custom
                if '_custom' in resource_raw and 'value' in resource_raw['_custom']:
                    resource_id = resource_raw['_custom']['value'].get('id')
                else:
                    resource_id = resource_raw.get("id")
        
        if not resource_id:
            return JsonResponse(
                {"success": False, "error": "resource_id es requerido"}, status=400
            )

        # Extraer project_id
        project_id = data.get('project_id') or data.get('project', {}).get('id')
        if not project_id:
            return JsonResponse(
                {"success": False, "error": "project_id es requerido"}, status=400
            )

        try:
            project = get_object_or_404(Project, id=project_id, is_active=True)
            resource = get_object_or_404(
                ResourceItem, id=resource_id, is_active=True
            )

            if resource.stst_status_disponibility == "RENTADO":
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"El recurso {resource.code} ya está rentado",
                    },
                    status=400,
                )

            try:
                operation_start = datetime.strptime(
                    data["operation_start_date"], "%Y-%m-%d"
                ).date()
            except (ValueError, KeyError):
                return JsonResponse(
                    {
                        "success": False,
                        "error": "operation_start_date inválido o faltante (YYYY-MM-DD)",
                    },
                    status=400,
                )

            operation_end = None
            if data.get("operation_end_date"):
                try:
                    operation_end = datetime.strptime(
                        data["operation_end_date"], "%Y-%m-%d"
                    ).date()
                    if operation_end < operation_start:
                        return JsonResponse(
                            {
                                "success": False,
                                "error": "operation_end_date no puede ser "
                                "anterior a operation_start_date",
                            },
                            status=400,
                        )
                except ValueError:
                    return JsonResponse(
                        {
                            "success": False,
                            "error": "operation_end_date inválido (YYYY-MM-DD)",
                        },
                        status=400,
                    )

            try:
                cost = Decimal(str(data.get("cost", 0))).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            except (InvalidOperation, TypeError, ValueError):
                return JsonResponse(
                    {
                        "success": False,
                        "error": "cost inválido. Debe ser numérico con hasta 2 decimales",
                    },
                    status=400,
                )

            try:
                interval_days = int(data.get("interval_days", 0))
                if interval_days < 0:
                    raise ValueError
            except (TypeError, ValueError):
                return JsonResponse(
                    {
                        "success": False,
                        "error": "interval_days inválido. Debe ser un entero no negativo",
                    },
                    status=400,
                )

            # Procesar maintenance_cost si existe
            maintenance_cost = Decimal("0.00")
            if data.get("maintenance_cost"):
                try:
                    maintenance_cost = Decimal(str(data["maintenance_cost"])).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                except (InvalidOperation, TypeError, ValueError):
                    return JsonResponse(
                        {
                            "success": False,
                            "error": "maintenance_cost inválido. Debe ser numérico",
                        },
                        status=400,
                    )

            project_resource = ProjectResourceItem(
                project=project,
                resource_item=resource,
                detailed_description=data.get("detailed_description") or data.get("resource_display_name"),
                cost=cost,
                interval_days=interval_days,
                operation_start_date=operation_start,
                operation_end_date=(
                    operation_end if operation_end else project.end_date
                ),
            )

            # Agregar maintenance_cost si el modelo lo soporta
            if hasattr(project_resource, 'maintenance_cost'):
                project_resource.maintenance_cost = maintenance_cost

            if getattr(request, "user", None) and request.user.is_authenticated:
                project_resource.created_by = request.user

            resource.stst_status_disponibility = "RENTADO"
            resource.stst_current_location = (
                project.location
                or f"Proyecto {getattr(project.partner, 'name', '')}".strip()
                or "Proyecto"
            )
            resource.stst_current_project_id = project.id

            today = date.today()
            resource.stst_commitment_date = (
                operation_start if operation_start > today else today
            )
            resource.stst_release_date = (
                operation_end if operation_end else project.end_date
            )

            if getattr(request, "user", None) and request.user.is_authenticated:
                resource.updated_by = request.user

            project_resource.full_clean()
            resource.full_clean()

            project_resource.save()
            resource.save()

            return JsonResponse({"success": True, "id": project_resource.id}, status=201)

        except ValidationError as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def _serialize(self, project_resource):
        """Serializar ProjectResourceItem a JSON."""
        return {
            "id": project_resource.id,
        }
