from django.http import JsonResponse
from django.views import View
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.SheetProject import SheetProject
from projects.models.Project import Project, ProjectResourceItem
from accounts.models.Technical import Technical
from equipment.models.Vehicle import Vehicle
import json
from datetime import date, datetime


class CreateCustodyChainAPI(View):
    """Crear una nueva cadena de custodia."""

    def serialize_date(self, value):
        """Serializa fechas y datetimes a formato ISO"""
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        return value

    def post(self, request):
        """Crear una cadena de custodia con todos sus detalles."""
        data = json.loads(request.body)

        technical_id = data.get("technical_id")
        vehicle_id = data.get("vehicle_id")
        project_id = data.get("project_id")
        resource_ids = data.get("resources", [])

        if not technical_id or not vehicle_id or not project_id:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Faltan datos requeridos: technical_id, vehicle_id, project_id",
                },
                status=400,
            )

        if not resource_ids or len(resource_ids) == 0:
            return JsonResponse(
                {"success": False, "error": "Debe seleccionar al menos un recurso"},
                status=400,
            )

        try:
            technical = Technical.objects.get(id=technical_id, is_active=True)
        except Technical.DoesNotExist:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Técnico con ID {technical_id} no encontrado",
                },
                status=404,
            )

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Vehículo con ID {vehicle_id} no encontrado",
                },
                status=404,
            )

        try:
            project = Project.objects.get(id=project_id, is_active=True)
        except Project.DoesNotExist:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Proyecto con ID {project_id} no encontrado",
                },
                status=404,
            )

        sheet_project = (
            SheetProject.objects.filter(project=project, is_active=True)
            .order_by("-id")
            .first()
        )

        if not sheet_project:
            return JsonResponse(
                {
                    "success": False,
                    "error": "No hay una planilla activa para este proyecto",
                },
                status=400,
            )

        valid_resources = []
        for resource_id in resource_ids:
            try:
                resource = ProjectResourceItem.objects.get(
                    id=resource_id, project=project, is_active=True
                )
                valid_resources.append(resource)
            except ProjectResourceItem.DoesNotExist:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Recurso con ID {resource_id} no encontrado o no pertenece al proyecto",
                    },
                    status=404,
                )

        custody_chain = CustodyChain(
            technical=technical,
            vehicle=vehicle,
            sheet_project=sheet_project,
            consecutive=CustodyChain.get_next_consecutive(),
            activity_date=data.get("activity_date"),
            issue_date=data.get("issue_date"),
            status=data.get("status", "DRAFT"),
            start_time=data.get("start_time") if data.get("start_time") else None,
            end_time=data.get("end_time") if data.get("end_time") else None,
            time_duration=float(data.get("duration_hours", 0)),
            location=data.get("location", ""),
            contact_name=data.get("contact_name", ""),
            dni_contact=data.get("dni_contact", ""),
            contact_position=data.get("contact_position", ""),
            date_contact=data.get("date_contact") if data.get("date_contact") else None,
            driver_name=data.get("driver_name", ""),
            dni_driver=data.get("dni_driver", ""),
            driver_position=data.get("driver_position", ""),
            driver_date=data.get("driver_date") if data.get("driver_date") else None,
            total_gallons=int(float(data.get("total_gallons", 0))),
            total_barrels=int(float(data.get("total_barrels", 0))),
            total_cubic_meters=int(float(data.get("total_cubic_meters", 0))),
            have_logistic=data.get("have_logistic", "NA"),
            notes=data.get("notes", "")
        )
        custody_chain.save()

        # Crear los detalles y recopilar la información
        details_data = []
        for resource in valid_resources:
            detail = ChainCustodyDetail(
                custody_chain=custody_chain,
                project_resource=resource
            )
            detail.save()
            
            detail_data = {
                "id": detail.id,
                "project_resource_id": resource.id,
                "project_resource": {
                    "id": resource.id,
                    "resource_item_id": resource.resource_item.id if resource.resource_item else None,
                    "resource_item_name": resource.resource_item.name if resource.resource_item else None,
                },
            }
            details_data.append(detail_data)

        # Construir el objeto completo de respuesta
        response_data = {
            "custody_chain": {
                "id": custody_chain.id,
                "consecutive": custody_chain.consecutive,
                "activity_date": self.serialize_date(custody_chain.activity_date),
                "location": custody_chain.location,
                "issue_date": self.serialize_date(custody_chain.issue_date),
                "status": custody_chain.status,
                "start_time": self.serialize_date(custody_chain.start_time),
                "end_time": self.serialize_date(custody_chain.end_time),
                "time_duration": float(custody_chain.time_duration) if custody_chain.time_duration is not None else None,
                "have_logistic": custody_chain.have_logistic,
                "contact_name": custody_chain.contact_name,
                "dni_contact": custody_chain.dni_contact,
                "contact_position": custody_chain.contact_position,
                "date_contact": self.serialize_date(custody_chain.date_contact),
                "driver_name": custody_chain.driver_name,
                "dni_driver": custody_chain.dni_driver,
                "driver_position": custody_chain.driver_position,
                "driver_date": self.serialize_date(custody_chain.driver_date),
                "total_gallons": custody_chain.total_gallons,
                "total_barrels": custody_chain.total_barrels,
                "total_cubic_meters": custody_chain.total_cubic_meters,
                "sheet_project_id": custody_chain.sheet_project_id,
            },
            "technical": {
                "id": technical.id,
                "first_name": technical.first_name,
                "last_name": technical.last_name,
            },
            "vehicle": {
                "id": vehicle.id,
                "no_plate": vehicle.no_plate,
                "brand": vehicle.brand,
                "model": vehicle.model,
            },
            "details": details_data,
            "details_count": len(details_data),
        }

        return JsonResponse(
            {
                "success": True,
                "message": "Cadena de custodia creada exitosamente",
                "data": response_data,
            },
            status=201,
        )
