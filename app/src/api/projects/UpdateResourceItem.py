from django.http import JsonResponse
from django.views import View
import json

from projects.models.Project import ProjectResourceItem


class UpdateResourceItemAPI(View):
	"""API para actualizar un recurso de un proyecto."""

	def put(self, request, resource_item_id):
		"""Actualizar un recurso de un proyecto."""
		data = json.loads(request.body)
		project_resource = ProjectResourceItem.objects.get(id=resource_item_id)

		if "cost" in data:
			project_resource.cost = data["cost"]
		if "interval_days" in data:
			project_resource.interval_days = data["interval_days"]
		if "operation_start_date" in data:
			project_resource.operation_start_date = data["operation_start_date"]
		if "is_retired" in data:
			project_resource.is_retired = data["is_retired"]
		if "retirement_date" in data:
			project_resource.retirement_date = data["retirement_date"]
		if "retirement_reason" in data:
			project_resource.retirement_reason = data["retirement_reason"]

		project_resource.save()

		response_data = {
			"id": project_resource.id,
			"cost": float(project_resource.cost),
			"interval_days": project_resource.interval_days,
			"operation_start_date": (
				project_resource.operation_start_date.isoformat()
				if project_resource.operation_start_date
				else None
			),
			"is_retired": project_resource.is_retired,
			"retirement_date": (
				project_resource.retirement_date.isoformat()
				if project_resource.retirement_date
				else None
			),
			"retirement_reason": project_resource.retirement_reason,
		}

		return JsonResponse({"success": True, "data": response_data})
