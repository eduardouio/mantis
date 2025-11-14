from django.http import JsonResponse
from django.views import View
from equipment.models.Vehicle import Vehicle
from equipment.models.PassVehicle import PassVehicle
from equipment.models.CertificationVehicle import CertificationVehicle
import json
from django.db.models import Prefetch


class GetVehiclesAvaliablesAPI(View):
    """API para obtener vehículos disponibles."""

    def get(self, request):
        """Obtener la lista de vehículos activos con sus pases y permisos."""
        vehicles_qs = Vehicle.get_all().prefetch_related(
            Prefetch(
                "passvehicle_set",
                queryset=PassVehicle.objects.filter(is_active=True),
                to_attr="passes",
            ),
            Prefetch(
                "certificationvehicle_set",
                queryset=CertificationVehicle.objects.filter(is_active=True),
                to_attr="certifications",
            ),
        )

        def serialize_date(d):
            return d.isoformat() if d else None

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

        result = []
        for v in vehicles_qs:
            passes = [
                {
                    "id": p.id,
                    "bloque": p.bloque,
                    "fecha_caducidad": serialize_date(p.fecha_caducidad),
                    "meta": serialize_meta(p),
                }
                for p in getattr(v, "passes", [])
            ]
            certificaciones = [
                {
                    "id": c.id,
                    "name": c.name,
                    "name_display": c.get_name_display(),
                    "date_start": serialize_date(c.date_start),
                    "date_end": serialize_date(c.date_end),
                    "description": c.description,
                    "meta": serialize_meta(c),
                }
                for c in getattr(v, "certifications", [])
            ]
            result.append(
                {
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
                    "due_date_technical_review": serialize_date(
                        v.due_date_technical_review
                    ),
                    "nro_poliza": v.nro_poliza,
                    "insurance_company": v.insurance_company,
                    "insurance_expiration_date": serialize_date(
                        v.insurance_expiration_date
                    ),
                    "insurance_issue_date": serialize_date(v.insurance_issue_date),
                    "date_satellite": serialize_date(v.date_satellite),
                    "due_date_satellite": serialize_date(v.due_date_satellite),
                    "serial_number": v.serial_number,
                    "engine_number": v.engine_number,
                    "chassis_number": v.chassis_number,
                    "passes": passes,
                    "certifications": certificaciones,
                    "notes": v.notes,
                    "created_at": serialize_date(v.created_at),
                    "updated_at": serialize_date(v.updated_at),
                    "is_active": v.is_active,
                    "is_deleted": v.is_deleted,
                    "id_user_created": v.id_user_created,
                    "id_user_updated": v.id_user_updated,
                    "meta": serialize_meta(v),
                }
            )

        return JsonResponse({"vehicles": result})
