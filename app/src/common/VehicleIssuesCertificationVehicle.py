from datetime import date
from django.utils import timezone
from equipment.models import CertificationVehicle, Vehicle


class VehicleIssuesCertificationVehicle:
    WARNING_30 = 30
    WARNING_10 = 10

    @classmethod
    def _evaluate(cls, expires_on: date):
        """Devuelve (status, days_left) o (None, None) si no aplica."""
        if not expires_on:
            return None, None
        today = date.today()
        days_left = (expires_on - today).days
        if days_left < 0:
            return 'expired', days_left
        if days_left <= cls.WARNING_10:
            return 'due_10', days_left
        if days_left <= cls.WARNING_30:
            return 'due_30', days_left
        return None, None

    @classmethod
    def issues_for(cls, vehicle: Vehicle):
        """Lista de alertas de certificaciones para un vehículo."""
        issues = []
        certifications = CertificationVehicle.objects.filter(
            vehicle=vehicle,
            is_active=True,
            date_end__isnull=False
        )
        
        for cert in certifications:
            status, days = cls._evaluate(cert.date_end)
            if status:
                issues.append({
                    'field': 'date_end',
                    'label': f"Certificación {cert.get_name_display()}",
                    'status': status,          # expired | due_10 | due_30
                    'days_left': days,
                    'expires_on': cert.date_end,
                    'certification_id': cert.id,
                    'vehicle_id': vehicle.id,
                    'vehicle_plate': vehicle.no_plate,
                    'certification_type': cert.name,
                })
        return issues

    @classmethod
    def issues_all(cls, queryset=None):
        """Alertas de certificaciones para todos los vehículos (o queryset provisto)."""
        qs = queryset if queryset is not None else Vehicle.objects.all()
        all_issues = []
        for vehicle in qs:
            all_issues.extend(cls.issues_for(vehicle))
        return all_issues
