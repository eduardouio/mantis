from django.http import JsonResponse
from django.views import View
from projects.models.SheetProject import SheetProject
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.Project import Project
from datetime import date, datetime


class AllInfoProjectAPI(View):
    """Retorna todas las cadenas de custodia asociadas a un proyecto con estructura completa."""

    def get(self, request, project_id):
        try:
            try:
                project = Project.objects.select_related('partner').get(
                    pk=project_id, is_active=True, is_deleted=False
                )
            except Project.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Proyecto no encontrado."}, 
                    status=404
                )

            sheets = (
                SheetProject.objects.filter(
                    project_id=project_id, is_active=True, is_deleted=False
                )
                .select_related("project")
                .order_by("-period_start")
            )

            def serialize_date(value):
                if isinstance(value, (date, datetime)):
                    return value.isoformat()
                return value

            def get_base_metadata(obj):
                """Extrae los metadatos del BaseModel"""
                return {
                    "notes": obj.notes,
                    "created_at": serialize_date(obj.created_at),
                    "updated_at": serialize_date(obj.updated_at),
                    "is_active": obj.is_active,
                    "is_deleted": obj.is_deleted,
                    "id_user_created": obj.id_user_created,
                    "id_user_updated": obj.id_user_updated,
                }

            work_orders = []

            for sheet in sheets:

                custody_chains = (
                    CustodyChain.objects.filter(
                        sheet_project_id=sheet.id, is_active=True, is_deleted=False
                    )
                    .select_related("technical", "vehicle", "sheet_project")
                    .order_by("-activity_date", "-consecutive")
                )

                custody_chains_data = []

                for chain in custody_chains:

                    chain_details = ChainCustodyDetail.objects.filter(
                        custody_chain_id=chain.id, is_active=True, is_deleted=False
                    ).select_related(
                        "project_resource", "project_resource__resource_item"
                    )

                    details_data = []
                    for detail in chain_details:
                        detail_data = {
                            "id": detail.id,
                            "project_resource_id": detail.project_resource.id,
                            "project_resource": {
                                "id": detail.project_resource.id,
                                "resource_item_id": detail.project_resource.resource_item.id,
                                "resource_item_name": (
                                    detail.project_resource.resource_item.name
                                    if detail.project_resource.resource_item
                                    else None
                                ),
                            },
                            "metadata": get_base_metadata(detail),
                        }
                        details_data.append(detail_data)

                    chain_data = {
                        "id": chain.id,
                        "consecutive": chain.consecutive,
                        "activity_date": serialize_date(chain.activity_date),
                        "location": chain.location,
                        "issue_date": serialize_date(chain.issue_date),
                        "status": chain.status,
                        "start_time": serialize_date(chain.start_time),
                        "end_time": serialize_date(chain.end_time),
                        "time_duration": (
                            float(chain.time_duration)
                            if chain.time_duration is not None
                            else None
                        ),
                        "have_logistic": chain.have_logistic,
                        "contact_name": chain.contact_name,
                        "dni_contact": chain.dni_contact,
                        "contact_position": chain.contact_position,
                        "date_contact": serialize_date(chain.date_contact),
                        "driver_name": chain.driver_name,
                        "dni_driver": chain.dni_driver,
                        "driver_position": chain.driver_position,
                        "driver_date": serialize_date(chain.driver_date),
                        "total_gallons": chain.total_gallons,
                        "total_barrels": chain.total_barrels,
                        "total_cubic_meters": chain.total_cubic_meters,
                        "sheet_project_id": chain.sheet_project_id,
                        "technical": (
                            {
                                "id": chain.technical.id,
                                "first_name": chain.technical.first_name,
                                "last_name": chain.technical.last_name,
                            }
                            if chain.technical
                            else None
                        ),
                        "vehicle": (
                            {
                                "id": chain.vehicle.id,
                                "no_plate": chain.vehicle.no_plate,
                                "brand": chain.vehicle.brand,
                                "model": chain.vehicle.model,
                            }
                            if chain.vehicle
                            else None
                        ),
                        "details": details_data,
                        "details_count": len(details_data),
                        "metadata": get_base_metadata(chain),
                    }
                    custody_chains_data.append(chain_data)

                work_order_data = {
                    "id": sheet.id,
                    "series_code": sheet.series_code,
                    "issue_date": serialize_date(sheet.issue_date),
                    "period_start": serialize_date(sheet.period_start),
                    "period_end": serialize_date(sheet.period_end),
                    "status": sheet.status,
                    "service_type": sheet.service_type,
                    "total_gallons": sheet.total_gallons,
                    "total_barrels": sheet.total_barrels,
                    "total_cubic_meters": sheet.total_cubic_meters,
                    "client_po_reference": sheet.client_po_reference,
                    "contact_reference": sheet.contact_reference,
                    "contact_phone_reference": sheet.contact_phone_reference,
                    "final_disposition_reference": sheet.final_disposition_reference,
                    "invoice_reference": sheet.invoice_reference,
                    "subtotal": float(sheet.subtotal),
                    "tax_amount": float(sheet.tax_amount),
                    "total": float(sheet.total),
                    "custody_chains": custody_chains_data,
                    "custody_chains_count": len(custody_chains_data),
                    "metadata": get_base_metadata(sheet),
                }
                work_orders.append(work_order_data)

            project_data = {
                "id": project.id,
                "partner_id": project.partner.id,
                "partner_name": project.partner.name,
                "location": project.location,
                "cardinal_point": project.cardinal_point,
                "contact_name": project.contact_name,
                "contact_phone": project.contact_phone,
                "start_date": serialize_date(project.start_date),
                "end_date": serialize_date(project.end_date) if project.end_date else None,
                "is_closed": project.is_closed,
            }

            response_data = {
                "project": project_data,
                "work_orders": work_orders,
                "work_orders_count": len(work_orders),
                "total_custody_chains": sum(
                    wo["custody_chains_count"] for wo in work_orders
                ),
            }

            return JsonResponse({"success": True, "data": response_data})

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Error al consultar las cadenas de custodia: {str(e)}",
                },
                status=500,
            )
