from datetime import date
from accounts.models import Technical


class TechnicalIssuesCheck:
    WARNING_30 = 30
    WARNING_10 = 10

    FIELD_LABELS = {
        'license_expiry_date': 'Licencia de conducir',
        'defensive_driving_certificate_expiry_date': 'Certificado de manejo defensivo',
        'mae_certificate_expiry_date': 'Certificado MAE',
        'medical_certificate_expiry_date': 'Certificado médico',
        'quest_end_date': 'Certificado Quest',
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
        return 'valid', days_left

    @classmethod
    def issues_for(cls, technical: Technical):
        """Lista de alertas para un técnico."""
        issues = []
        for field, label in cls.FIELD_LABELS.items():
            status, days = cls._evaluate(getattr(technical, field, None))
            if status:
                issues.append({
                    'field': field,
                    'label': label,
                    'status': status,        # expired | due_10 | due_30
                    'days_left': days,
                    'expires_on': getattr(technical, field),
                    'technical_id': technical.id,
                    'technical_name': f"{technical.first_name} {technical.last_name}",
                })
        return issues

    @classmethod
    def issues_all(cls, queryset=None):
        """Alertas para todos los técnicos (o queryset provisto)."""
        qs = queryset if queryset is not None else Technical.objects.all()
        all_issues = []
        for tech in qs:
            all_issues.extend(cls.issues_for(tech))
        return all_issues
