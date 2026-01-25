from django.views.generic import TemplateView
from equipment.models.Vehicle import Vehicle
from equipment.models.PassVehicle import PassVehicle
from equipment.models.CertificationVehicle import CertificationVehicle
from common.VehicleIssuesCheck import VehicleIssuesCheck
from common.AppLoggin import loggin_event
from datetime import date


class VehiclesByStatusView(TemplateView):
    template_name = "reports/vehicles_status_report.html"

    def get_context_data(self, **kwargs):
        loggin_event("Generando reporte de vehículos por estado")
        context = super().get_context_data(**kwargs)

        all_vehicles = Vehicle.objects.filter(is_active=True, is_deleted=False)

        all_vehicles_list = []

        stats = {
            "total": 0,
            "disponible": 0,
            "mantenimiento": 0,
            "standby": 0,
            "con_alertas": 0,
            "sin_alertas": 0,
        }

        for vehicle in all_vehicles:

            issues = VehicleIssuesCheck.issues_for(vehicle)

            passes = PassVehicle.get_by_vehicle(vehicle.id)
            passes_list = []
            for pass_obj in passes:
                days_to_expire = None
                if pass_obj.fecha_caducidad:
                    days_to_expire = (pass_obj.fecha_caducidad - date.today()).days
                passes_list.append(
                    {
                        "bloque": pass_obj.bloque,
                        "fecha_caducidad": pass_obj.fecha_caducidad,
                        "days_to_expire": days_to_expire,
                        "is_expired": (
                            days_to_expire < 0 if days_to_expire is not None else False
                        ),
                        "is_expiring_soon": (
                            0 <= days_to_expire <= 30
                            if days_to_expire is not None
                            else False
                        ),
                    }
                )

            certifications = CertificationVehicle.objects.filter(
                vehicle=vehicle, is_active=True
            )
            certifications_list = []
            for cert in certifications:
                days_to_expire = None
                if cert.date_end:
                    days_to_expire = (cert.date_end - date.today()).days
                certifications_list.append(
                    {
                        "name": cert.get_name_display(),
                        "date_start": cert.date_start,
                        "date_end": cert.date_end,
                        "days_to_expire": days_to_expire,
                        "is_expired": (
                            days_to_expire < 0 if days_to_expire is not None else False
                        ),
                    }
                )

            expired_issues = [i for i in issues if i["status"] == "expired"]
            due_10_issues = [i for i in issues if i["status"] == "due_10"]
            due_30_issues = [i for i in issues if i["status"] == "due_30"]

            status = vehicle.status_vehicle or "DISPONIBLE"

            if status == "DISPONIBLE":
                status_class = "success"
                stats["disponible"] += 1
            elif status == "EN MANTENIMIENTO":
                status_class = "warning"
                stats["mantenimiento"] += 1
            elif status == "STANBY":
                status_class = "secondary"
                stats["standby"] += 1
            else:
                status_class = "info"
                stats["disponible"] += 1

            has_alerts = len(issues) > 0
            if has_alerts:
                stats["con_alertas"] += 1
            else:
                stats["sin_alertas"] += 1

            stats["total"] += 1

            vehicle_data = {
                "vehicle": vehicle,
                "status_display": status,
                "status_class": status_class,
                "issues": issues,
                "expired_count": len(expired_issues),
                "due_10_count": len(due_10_issues),
                "due_30_count": len(due_30_issues),
                "passes": passes_list,
                "certifications": certifications_list,
                "has_alerts": has_alerts,
            }

            all_vehicles_list.append(vehicle_data)

        context.update(
            {
                "all_vehicles": all_vehicles_list,
                "stats": stats,
            }
        )

        return context
