from django.http import JsonResponse
from django.views import View
import json
from datetime import date

from projects.models.Project import ProjectResourceItem


class UpdateResourceItemAPI(View):
	"""API para actualizar un recurso de un proyecto."""

	def put(self, request):
		"""Actualizar un recurso de un proyecto."""
		data = json.loads(request.body)
		project_resource = ProjectResourceItem.get_by_id(data.get("id"))
		if not project_resource:
			return JsonResponse(
				{"error": "Recurso del proyecto no encontrado."},
				status=500
			)

		project_resource.cost =  data['cost']
		project_resource.interval_days =  data['interval_days']
		project_resource.operation_start_date =  data['operation_start_date']
		project_resource.is_retired =  data['is_retired']


		if data['is_retired']:
			project_resource.retirement_date =  data['retirement_date']
			project_resource.retirement_reason =  data['retirement_reason']
			project_resource.operation_end_date =  data['retirement_date']
			project_resource.is_active = False
			project_resource.save()
			self.liberate_resource(project_resource.resource_item)
			return JsonResponse(
				{"message": "Recurso del proyecto actualizado y liberado correctamente."},
				status=200
			)
	
		project_resource.save()
		return JsonResponse(
			{"message": "Recurso del proyecto actualizado correctamente."},
			status=200
		)

	def liberate_resource(self, resource):
		resource.stst_current_location = "EN BASE PEISOL"
		resource.stst_release_date = date.today()
		resource.stst_current_project_id = None
		resource.stst_status_disponibility = "DISPONIBLE"
		resource.save()