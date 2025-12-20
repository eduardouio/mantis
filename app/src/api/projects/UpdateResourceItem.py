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

		project_resource.cost =  data.get('cost', 0.00)

		# Validación y asignación según tipo de frecuencia
		frequency_type = data.get('frequency_type', 'DAY')
		project_resource.frequency_type = frequency_type

		if frequency_type == 'DAY':
			interval = int(data.get('interval_days', 1))
			if interval < 1:
				return JsonResponse({"error": "El intervalo de días debe ser mayor a 0."}, status=400)
			project_resource.interval_days = interval
			project_resource.weekdays = None
			project_resource.monthdays = None
		
		elif frequency_type == 'WEEK':
			weekdays = data.get('weekdays')
			if not weekdays or not isinstance(weekdays, list) or len(weekdays) == 0:
				return JsonResponse({"error": "Debe seleccionar al menos un día de la semana."}, status=400)
			project_resource.interval_days = 0
			project_resource.weekdays = weekdays
			project_resource.monthdays = None
			
		elif frequency_type == 'MONTH':
			monthdays = data.get('monthdays')
			if not monthdays or not isinstance(monthdays, list) or len(monthdays) == 0:
				return JsonResponse({"error": "Debe seleccionar al menos un día del mes."}, status=400)
			project_resource.interval_days = 0
			project_resource.weekdays = None
			project_resource.monthdays = monthdays

		project_resource.detailed_description = data.get('detailed_description', project_resource.detailed_description)
		project_resource.operation_start_date =  data.get('operation_start_date')

		if data.get('is_retired'):
			project_resource.retirement_date =  data['retirement_date']
			project_resource.retirement_reason =  data['retirement_reason']
			project_resource.operation_end_date =  data['retirement_date']
			project_resource.is_retired = True
			project_resource.save()
			self.liberate_resource(project_resource.resource_item)
			return JsonResponse(
				{"message": "Recurso del proyecto actualizado y liberado correctamente.", "data": self._serialize(project_resource)},
				status=200
			)
	
		project_resource.save()
		return JsonResponse(
			{"message": "Recurso del proyecto actualizado correctamente.", "data": self._serialize(project_resource)},
			status=200
		)

	def liberate_resource(self, resource):
		resource.stst_current_location = "EN BASE PEISOL"
		resource.stst_release_date = date.today()
		resource.stst_current_project_id = None
		resource.stst_status_disponibility = "DISPONIBLE"
		resource.save()

	def _serialize(self, project_resource):
		def format_date(d):
			if not d:
				return None
			if isinstance(d, str):
				return d
			return d.isoformat()

		return {
			"id": project_resource.id,
			"project_id": project_resource.project.id,
			"type": project_resource.resource_item.type_equipment,
			"resource_item_id": project_resource.resource_item.id,
			"resource_item_code": project_resource.resource_item.code,
			"resource_item_name": project_resource.resource_item.name,
			"detailed_description": project_resource.detailed_description,
			"cost": project_resource.cost,
			"frequency_type": project_resource.frequency_type,
			"interval_days": project_resource.interval_days,
			"weekdays": project_resource.weekdays,
			"monthdays": project_resource.monthdays,
			"operation_start_date": format_date(project_resource.operation_start_date),
			"is_active": project_resource.is_active,
			"type_resource": project_resource.type_resource,
			"is_retired": project_resource.is_retired,
			"retirement_date": format_date(project_resource.retirement_date),
			"retirement_reason": project_resource.retirement_reason,
			"notes": project_resource.notes
		}