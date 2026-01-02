from datetime import date
from equipment.models import Vehicle


class VehicleIssuesCheck:
    WARNING_30 = 30
    WARNING_10 = 10

    FIELD_LABELS = {
        'due_date_cert_oper': 'Certificado de Operación',
        'due_date_matricula': 'Matrícula',
        'due_date_mtop': 'MTOP',
        'due_date_technical_review': 'Revisión Técnica',
        'insurance_expiration_date': 'Seguro',
        'due_date_satellite': 'Sistema Satelital',
    }

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
        """Lista de alertas para un vehículo."""
        issues = []
        for field, label in cls.FIELD_LABELS.items():
            status, days = cls._evaluate(getattr(vehicle, field, None))
            if status:
                issues.append({
                    'field': field,
                    'label': label,
                    'status': status,      # expired | due_10 | due_30
                    'days_left': days,
                    'expires_on': getattr(vehicle, field),
                    'vehicle_id': vehicle.id,
                    'vehicle_plate': vehicle.no_plate,
                })
        return issues

    @classmethod
    def issues_all(cls, queryset=None):
        """Alertas para todos los vehículos (o queryset provisto)."""
        qs = queryset if queryset is not None else Vehicle.objects.all()
        all_issues = []
        for vehicle in qs:
            all_issues.extend(cls.issues_for(vehicle))
        return all_issues
