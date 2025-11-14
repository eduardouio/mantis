from django.http import JsonResponse
from django.views import View
from projects.models.Project import Project
from projects.models.Partner import Partner


class ProjectData(View):
	"""Manejar datos básicos del proyecto."""

	def get(self, request, project_id):
		"""Obtener datos básicos del proyecto."""
		try:
			project = Project.objects.get(
				id=project_id, is_deleted=False, is_active=True
			)
			partner = Partner.objects.get(
				id=project.partner.id, is_deleted=False, is_active=True
			)

			data = {
				"id": project.id,
				"partner_id": partner.id,
				"partner_name": partner.name,
				"location": project.location,
				"cardinal_point": project.cardinal_point,
				"contact_name": project.contact_name,
				"contact_phone": project.contact_phone,
				"start_date": project.start_date.isoformat(),
				"end_date": project.end_date.isoformat() if project.end_date else None,
				"is_closed": project.is_closed,
			}

			return JsonResponse({"success": True, "data": data})

		except Project.DoesNotExist:
			return JsonResponse(
				{"success": False, "error": "Proyecto no encontrado."},
				status=404
			)
		except Exception as e:
			return JsonResponse(
				{"success": False, "error": str(e)},
				status=500
			)
