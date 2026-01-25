from django.http import JsonResponse
from django.views import View
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from projects.models.Project import Project, ProjectResourceItem
from equipment.models.Vehicle import Vehicle
from accounts.models.Technical import Technical
from decimal import Decimal
from datetime import date, datetime


class CustodyChainDetailAPI(View):
    """Detalle completo de una cadena de custodia con dependencias y metadatos."""

    def get(self, request, id):
        chain_id = id

        try:
            instance = (
                CustodyChain.objects.select_related(
                    "technical", "vehicle", "sheet_project"
                )
                .prefetch_related(
                    "chaincustodydetail_set__project_resource",
                    "chaincustodydetail_set__project_resource__project",
                    "chaincustodydetail_set__project_resource__project__partner",
                    "chaincustodydetail_set__project_resource__resource_item",
                )
                .get(pk=chain_id)
            )
        except CustodyChain.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Cadena de custodia no encontrada."},
                status=404,
            )

        def serialize_date(value):
            if isinstance(value, (date, datetime)):
                return value.isoformat()
            return value

        def serialize_meta(obj):
            return {
                "notes": getattr(obj, "notes", None),
                "created_at": serialize_date(getattr(obj, "created_at", None)),
                "updated_at": serialize_date(getattr(obj, "updated_at", None)),
                "is_active": getattr(obj, "is_active", None),
                "is_deleted": getattr(obj, "is_deleted", None),
                "id_user_created": getattr(obj, "id_user_created", None),
                "id_user_updated": getattr(obj, "id_user_updated", None),
            }

        def serialize_chain(c: CustodyChain):
            return {
                "id": c.id,
                "consecutive": c.consecutive,
                "activity_date": serialize_date(c.activity_date),
                "location": c.location,
                "issue_date": serialize_date(c.issue_date),
                "status": c.status,
                "start_time": serialize_date(c.start_time),
                "end_time": serialize_date(c.end_time),
                "time_duration": float(c.time_duration) if c.time_duration is not None else None,
                "have_logistic": c.have_logistic,
                "contact_name": c.contact_name,
                "dni_contact": c.dni_contact,
                "contact_position": c.contact_position,
                "date_contact": serialize_date(c.date_contact),
                "driver_name": c.driver_name,
                "dni_driver": c.dni_driver,
                "driver_position": c.driver_position,
                "driver_date": serialize_date(c.driver_date),
                "total_gallons": c.total_gallons,
                "total_barrels": c.total_barrels,
                "total_cubic_meters": c.total_cubic_meters,
                "meta": serialize_meta(c),
            }

        def serialize_technical(t: Technical | None):
            if not t:
                return None
            return {
                "id": t.id,
                "first_name": t.first_name,
                "last_name": t.last_name,
                "email": t.email,
                "work_area": t.work_area,
                "work_area_display": getattr(t, "get_work_area_display", lambda: t.work_area)(),
                "dni": t.dni,
                "nro_phone": t.nro_phone,
                "date_joined": serialize_date(t.date_joined),
                "birth_date": serialize_date(t.birth_date),
                "license_issue_date": serialize_date(t.license_issue_date),
                "license_expiry_date": serialize_date(t.license_expiry_date),
                "defensive_driving_certificate_issue_date": serialize_date(t.defensive_driving_certificate_issue_date),
                "defensive_driving_certificate_expiry_date": serialize_date(t.defensive_driving_certificate_expiry_date),
                "mae_certificate_issue_date": serialize_date(t.mae_certificate_issue_date),
                "mae_certificate_expiry_date": serialize_date(t.mae_certificate_expiry_date),
                "medical_certificate_issue_date": serialize_date(t.medical_certificate_issue_date),
                "medical_certificate_expiry_date": serialize_date(t.medical_certificate_expiry_date),
                "is_iess_affiliated": t.is_iess_affiliated,
                "has_life_insurance_policy": t.has_life_insurance_policy,
                "quest_ncst_code": t.quest_ncst_code,
                "quest_instructor": t.quest_instructor,
                "quest_start_date": serialize_date(t.quest_start_date),
                "quest_end_date": serialize_date(t.quest_end_date),
                "meta": serialize_meta(t),
            }

        def serialize_vehicle(v: Vehicle | None):
            if not v:
                return None
            return {
                "id": v.id,
                "brand": v.brand,
                "model": v.model,
                "type_vehicle": v.type_vehicle,
                "year": v.year,
                "no_plate": v.no_plate,
                "status_vehicle": v.status_vehicle,
                "status_cert_oper": v.status_cert_oper,
                "date_cert_oper": serialize_date(v.date_cert_oper),
                "due_date_cert_oper": serialize_date(v.due_date_cert_oper),
                "date_matricula": serialize_date(v.date_matricula),
                "due_date_matricula": serialize_date(v.due_date_matricula),
                "date_mtop": serialize_date(v.date_mtop),
                "due_date_mtop": serialize_date(v.due_date_mtop),
                "date_technical_review": serialize_date(v.date_technical_review),
                "due_date_technical_review": serialize_date(v.due_date_technical_review),
                "nro_poliza": v.nro_poliza,
                "insurance_company": v.insurance_company,
                "insurance_expiration_date": serialize_date(v.insurance_expiration_date),
                "insurance_issue_date": serialize_date(v.insurance_issue_date),
                "date_satellite": serialize_date(v.date_satellite),
                "due_date_satellite": serialize_date(v.due_date_satellite),
                "serial_number": v.serial_number,
                "engine_number": v.engine_number,
                "chassis_number": v.chassis_number,
                "meta": serialize_meta(v),
            }

        def serialize_sheet_project(s):
            if not s:
                return None
            return {
                "id": s.id,
                "project_id": s.project_id,
                "issue_date": serialize_date(s.issue_date),
                "period_start": serialize_date(s.period_start),
                "period_end": serialize_date(s.period_end),
                "status": s.status,
                "series_code": s.series_code,
                "secuence_prefix": s.secuence_prefix,
                "secuence_year": s.secuence_year,
                "secuence_number": s.secuence_number,
                "service_type": s.service_type,
                "total_gallons": s.total_gallons,
                "total_barrels": s.total_barrels,
                "total_cubic_meters": s.total_cubic_meters,
                "client_po_reference": s.client_po_reference,
                "contact_reference": s.contact_reference,
                "contact_phone_reference": s.contact_phone_reference,
                "final_disposition_reference": s.final_disposition_reference,
                "invoice_reference": s.invoice_reference,
                "subtotal": float(s.subtotal) if s.subtotal is not None else 0.0,
                "tax_amount": float(s.tax_amount) if s.tax_amount is not None else 0.0,
                "total": float(s.total) if s.total is not None else 0.0,
                "meta": serialize_meta(s),
            }

        def serialize_project_resource(pr: ProjectResourceItem):
            return {
                "id": pr.id,
                "project": {
                    "id": pr.project_id,
                    "partner_id": getattr(pr.project.partner, "id", None),
                    "partner_name": getattr(pr.project.partner, "name", None),
                    "location": pr.project.location if hasattr(pr.project, "location") else None,
                    "meta": serialize_meta(pr.project),
                } if getattr(pr, "project", None) else {"id": pr.project_id},
                "resource_item": {
                    "id": pr.resource_item_id,
                    "name": getattr(pr.resource_item, "name", None),
                    "code": getattr(pr.resource_item, "code", None),
                    "type_equipment": getattr(pr.resource_item, "type_equipment", None),
                    "meta": serialize_meta(pr.resource_item),
                } if getattr(pr, "resource_item", None) else {"id": pr.resource_item_id},
                "type_resource": pr.type_resource,
                "detailed_description": pr.detailed_description,
                "cost": float(pr.cost) if pr.cost is not None else 0.0,
                "interval_days": pr.interval_days,
                "operation_start_date": serialize_date(pr.operation_start_date),
                "operation_end_date": serialize_date(pr.operation_end_date),
                "is_retired": pr.is_retired,
                "retirement_date": serialize_date(pr.retirement_date),
                "retirement_reason": pr.retirement_reason,
                "meta": serialize_meta(pr),
            }

        # Detalles de cadena con su ProjectResourceItem
        details_qs = (
            instance.chaincustodydetail_set
            .filter(is_active=True)
            .select_related(
                "project_resource__project__partner",
                "project_resource__resource_item",
            )
        )
        details = [
            {
                "id": d.id,
                "project_resource": serialize_project_resource(d.project_resource),
                "meta": serialize_meta(d),
            }
            for d in details_qs
        ]

        data = {
            "custody_chain": serialize_chain(instance),
            "technical": serialize_technical(instance.technical),
            "vehicle": serialize_vehicle(instance.vehicle),
            "sheet_project": serialize_sheet_project(instance.sheet_project),
            "details": details,
        }

        return JsonResponse({"success": True, "data": data})
