from datetime import date
from django.utils import timezone
from equipment.models import PassVehicle


class PassVehichleIssuesCheck:
    WARNING_30 = 30
    WARNING_10 = 10

    @classmethod
    def _evaluate(cls, expires_on: date):
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
    def issues_for(cls, pass_record: PassVehicle):
        status, days = cls._evaluate(getattr(pass_record, 'fecha_caducidad', None))
        if not status:
            return []
        return [{
            'field': 'fecha_caducidad',
            'label': f"Pase {pass_record.get_bloque_display()}",
            'status': status,          # expired | due_10 | due_30
            'days_left': days,
            'expires_on': pass_record.fecha_caducidad,
            'pass_id': pass_record.id,
            'vehicle_id': pass_record.vehicle_id,
            'vehicle_plate': getattr(pass_record.vehicle, 'no_plate', None),
            'bloque': pass_record.bloque,
        }]

    @classmethod
    def issues_all(cls, queryset=None):
        qs = queryset if queryset is not None else PassVehicle.objects.all()
        all_issues = []
        for record in qs:
            all_issues.extend(cls.issues_for(record))
        return all_issues
