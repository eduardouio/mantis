from django.http import JsonResponse
from django.views import View
from django.db import transaction
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.Project import ProjectResourceItem
from projects.models.SheetProject import SheetProject
from accounts.models.Technical import Technical
from equipment.models.Vehicle import Vehicle
from equipment.models.ResourceItem import ResourceItem
from decimal import Decimal
from datetime import datetime, date, time
import json


def get_equipment_code_and_abbreviation(project_resource):
    """Obtiene el código completo y la abreviatura del equipo.

    Args:
        project_resource: Instancia de ProjectResourceItem

    Returns:
        tuple: (code_equipment, equipment_abbreviation) o valores por defecto si no se encuentra
    """
    try:
        physical_code = project_resource.physical_equipment_code

        if not physical_code or physical_code == 0:
            return project_resource.detailed_description, "OT"

        resource_item = ResourceItem.objects.filter(
            id=physical_code, is_active=True
        ).first()

        if not resource_item or not resource_item.code:
            return project_resource.detailed_description, "OT"

        code_equipment = resource_item.code

        parts = code_equipment.split("-")
        equipment_abbreviation = parts[1] if len(parts) > 1 else "OT"

        return code_equipment, equipment_abbreviation
    except Exception:

        return project_resource.detailed_description, "OT"


class CustodyChainEditAPI(View):
    """API para actualizar cadena de custodia con sus detalles."""

    def put(self, request, id):
        return self._update_chain(request, id)

    def patch(self, request, id):
        return self._update_chain(request, id)

    def _update_chain(self, request, chain_id):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "JSON inválido."},
                status=400,
            )

        try:
            instance = CustodyChain.objects.get(pk=chain_id)
        except CustodyChain.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Cadena de custodia no encontrada."},
                status=404,
            )

        def parse_date(value):
            if not value:
                return None
            if isinstance(value, (date, datetime)):
                return value
            return datetime.strptime(value, "%Y-%m-%d").date()

        def parse_time(value):
            if not value:
                return None
            if isinstance(value, time):
                return value
            return datetime.strptime(value, "%H:%M:%S").time()

        def parse_decimal(value):
            if value is None:
                return None
            return Decimal(str(value))

        try:
            with transaction.atomic():

                chain_data = data.get("custody_chain", {})

                if "technical_id" in chain_data:
                    if chain_data["technical_id"]:
                        instance.technical = Technical.objects.get(
                            pk=chain_data["technical_id"]
                        )
                    else:
                        instance.technical = None

                if "vehicle_id" in chain_data:
                    if chain_data["vehicle_id"]:
                        instance.vehicle = Vehicle.objects.get(
                            pk=chain_data["vehicle_id"]
                        )
                    else:
                        instance.vehicle = None

                if "sheet_project_id" in chain_data:
                    instance.sheet_project = SheetProject.objects.get(
                        pk=chain_data["sheet_project_id"]
                    )

                if "consecutive" in chain_data:
                    instance.consecutive = chain_data["consecutive"]

                if "activity_date" in chain_data:
                    instance.activity_date = parse_date(chain_data["activity_date"])

                if "location" in chain_data:
                    instance.location = chain_data["location"]

                if "issue_date" in chain_data:
                    instance.issue_date = parse_date(chain_data["issue_date"])

                if "status" in chain_data:
                    instance.status = chain_data["status"]

                if "start_time" in chain_data:
                    instance.start_time = parse_time(chain_data["start_time"])

                if "end_time" in chain_data:
                    instance.end_time = parse_time(chain_data["end_time"])

                if "time_duration" in chain_data:
                    instance.time_duration = parse_decimal(chain_data["time_duration"])

                if "have_logistic" in chain_data:
                    instance.have_logistic = chain_data["have_logistic"]

                if "contact_name" in chain_data:
                    instance.contact_name = chain_data["contact_name"]

                if "dni_contact" in chain_data:
                    instance.dni_contact = chain_data["dni_contact"]

                if "contact_position" in chain_data:
                    instance.contact_position = chain_data["contact_position"]

                if "date_contact" in chain_data:
                    instance.date_contact = parse_date(chain_data["date_contact"])

                if "driver_name" in chain_data:
                    instance.driver_name = chain_data["driver_name"]

                if "dni_driver" in chain_data:
                    instance.dni_driver = chain_data["dni_driver"]

                if "driver_position" in chain_data:
                    instance.driver_position = chain_data["driver_position"]

                if "driver_date" in chain_data:
                    instance.driver_date = parse_date(chain_data["driver_date"])

                if "total_gallons" in chain_data:
                    instance.total_gallons = parse_decimal(chain_data["total_gallons"])

                if "total_barrels" in chain_data:
                    instance.total_barrels = parse_decimal(chain_data["total_barrels"])

                if "total_cubic_meters" in chain_data:
                    instance.total_cubic_meters = parse_decimal(chain_data["total_cubic_meters"])

                if "black_water" in chain_data:
                    instance.black_water = chain_data["black_water"]

                if "grey_water" in chain_data:
                    instance.grey_water = chain_data["grey_water"]

                if "clean_water" in chain_data:
                    instance.clean_water = chain_data["clean_water"]

                if "activated_sludge" in chain_data:
                    instance.activated_sludge = chain_data["activated_sludge"]

                if "treated_wastewater" in chain_data:
                    instance.treated_wastewater = chain_data["treated_wastewater"]

                if "organic_grease" in chain_data:
                    instance.organic_grease = chain_data["organic_grease"]

                meta = chain_data.get("meta", {})
                if "notes" in meta:
                    instance.notes = meta["notes"]

                instance.save()

                if "id_user_updated" in meta:
                    CustodyChain.objects.filter(pk=instance.pk).update(
                        id_user_updated=meta["id_user_updated"]
                    )

                details_data = data.get("details", [])

                # Obtener los IDs de recursos del proyecto que vienen en la solicitud
                incoming_project_resource_ids = [
                    d.get("project_resource_id") for d in details_data 
                    if d.get("project_resource_id")
                ]

                # Obtener todos los detalles existentes (activos e inactivos)
                existing_details = ChainCustodyDetail.objects.filter(
                    custody_chain=instance
                )
                
                # Desactivar los detalles que ya no están en la selección actual
                for detail in existing_details:
                    if detail.project_resource_id not in incoming_project_resource_ids:
                        if detail.is_active:
                            detail.is_active = False
                            detail.save()

                # Procesar cada recurso seleccionado
                for detail_data in details_data:
                    project_resource_id = detail_data.get("project_resource_id")

                    if not project_resource_id:
                        continue

                    try:
                        project_resource = ProjectResourceItem.objects.get(
                            pk=project_resource_id
                        )
                    except ProjectResourceItem.DoesNotExist:
                        continue

                    # Buscar si ya existe un detalle para este recurso (activo o inactivo)
                    existing_detail = ChainCustodyDetail.objects.filter(
                        custody_chain=instance,
                        project_resource_id=project_resource_id
                    ).first()

                    code_equipment, equipment_abbr = (
                        get_equipment_code_and_abbreviation(project_resource)
                    )

                    if existing_detail:
                        # Si existe, actualizarlo y reactivarlo si estaba inactivo
                        existing_detail.is_active = True
                        existing_detail.code_equipment = code_equipment
                        existing_detail.equipment = equipment_abbr
                        existing_detail.save()
                    else:
                        # Si no existe, crear uno nuevo
                        ChainCustodyDetail.objects.create(
                            custody_chain=instance,
                            project_resource=project_resource,
                            code_equipment=code_equipment,
                            equipment=equipment_abbr,
                        )

                return JsonResponse(
                    {
                        "success": True,
                        "message": "Cadena de custodia actualizada exitosamente.",
                        "data": {"id": instance.id},
                    }
                )

        except Technical.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Técnico no encontrado."},
                status=404,
            )
        except Vehicle.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Vehículo no encontrado."},
                status=404,
            )
        except SheetProject.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Hoja de proyecto no encontrada."},
                status=404,
            )
        except ProjectResourceItem.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Recurso de proyecto no encontrado."},
                status=404,
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error al actualizar: {str(e)}"},
                status=500,
            )
