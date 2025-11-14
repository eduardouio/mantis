from django.http import JsonResponse
from django.views import View
from django.db.models import Prefetch
from accounts.models.Technical import Technical
from accounts.models.PassTechnical import PassTechnical
from accounts.models.VaccinationRecord import VaccinationRecord

class GetTechnicalsAvaliablesAPI(View):
	"""Lista técnicos activos con sus pases y vacunas."""

	def get(self, request):
		qs = Technical.objects.filter(is_active=True).prefetch_related(
			Prefetch(
				'passtechnical_set',
				queryset=PassTechnical.objects.filter(is_active=True),
				to_attr='passes'
			),
			Prefetch(
				'vaccination_records',
				queryset=VaccinationRecord.objects.filter(is_active=True),
				to_attr='vaccines'
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

		data = []
		for t in qs:
			passes = [
				{
					"id": p.id,
					"bloque": p.bloque,
					"bloque_display": p.get_bloque_display(),
					"fecha_caducidad": serialize_date(p.fecha_caducidad),
					"meta": serialize_meta(p),
				}
				for p in getattr(t, 'passes', [])
			]
			vaccines = [
				{
					"id": v.id,
					"vaccine_type": v.vaccine_type,
					"vaccine_type_display": v.get_vaccine_type_display(),
					"batch_number": v.batch_number,
					"application_date": serialize_date(v.application_date),
					"dose_number": v.dose_number,
					"next_dose_date": serialize_date(v.next_dose_date),
					"days_to_next_dose": v.days_to_next_dose,
					"notes": v.notes,
					"meta": serialize_meta(v),
				}
				for v in getattr(t, 'vaccines', [])
			]
			data.append({
				"id": t.id,
				"first_name": t.first_name,
				"last_name": t.last_name,
				"email": t.email,
				"work_area": t.work_area,
				"work_area_display": t.get_work_area_display(),
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
				"notes": t.notes,
				"is_active": t.is_active,
				"is_deleted": t.is_deleted,
				"id_user_created": t.id_user_created,
				"id_user_updated": t.id_user_updated,
				"passes": passes,
				"vaccination_records": vaccines,
				"meta": serialize_meta(t),
			})

		return JsonResponse({"technicals": data})
