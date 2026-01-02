from datetime import date
from django.utils import timezone
from accounts.models import VaccinationRecord, Technical


class TechnicalVaccinesIssuesCheck:
    WARNING_30 = 30
    WARNING_10 = 10

    @classmethod
    def _evaluate(cls, next_dose_date: date):
        """Devuelve (status, days_left) o (None, None) si no aplica."""
        if not next_dose_date:
            return None, None
        today = timezone.localdate()
        days_left = (next_dose_date - today).days
        if days_left < 0:
            return 'expired', days_left
        if days_left <= cls.WARNING_10:
            return 'due_10', days_left
        if days_left <= cls.WARNING_30:
            return 'due_30', days_left
        return None, None

    @classmethod
    def issues_for(cls, technical: Technical):
        """Lista de alertas de vacunas para un técnico."""
        issues = []
        vaccination_records = VaccinationRecord.objects.filter(
            technical=technical,
            is_active=True,
            next_dose_date__isnull=False
        )
        
        for record in vaccination_records:
            status, days = cls._evaluate(record.next_dose_date)
            if status:
                issues.append({
                    'field': 'next_dose_date',
                    'label': f"Vacuna {record.get_vaccine_type_display()} - Dosis {record.dose_number or 'N/A'}",
                    'status': status,          # expired | due_10 | due_30
                    'days_left': days,
                    'expires_on': record.next_dose_date,
                    'vaccination_record_id': record.id,
                    'technical_id': technical.id,
                    'technical_name': f"{technical.first_name} {technical.last_name}",
                    'vaccine_type': record.vaccine_type,
                })
        return issues

    @classmethod
    def issues_all(cls, queryset=None):
        """Alertas de vacunas para todos los técnicos (o queryset provisto)."""
        qs = queryset if queryset is not None else Technical.objects.all()
        all_issues = []
        for tech in qs:
            all_issues.extend(cls.issues_for(tech))
        return all_issues
