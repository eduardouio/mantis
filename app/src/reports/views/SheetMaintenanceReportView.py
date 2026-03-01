from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.SheetMaintenance import SheetMaintenance


class SheetMaintenanceReportView(TemplateView):
	template_name = "reports/sheet_maintenance.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		sheet_id = kwargs.get("id")
		sheet = get_object_or_404(
			SheetMaintenance.objects.select_related(
				'project__partner',
				'responsible_technical',
				'resource_item',
			),
			pk=sheet_id
		)
		context["sheet"] = sheet
		return context
