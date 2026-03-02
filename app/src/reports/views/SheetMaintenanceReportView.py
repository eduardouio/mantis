from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.SheetMaintenance import SheetMaintenance
import textwrap


class SheetMaintenanceReportView(TemplateView):
	template_name = "reports/sheet_maintenance.html"

	def _split_text_lines(self, text, width=70, max_lines=6):
		content = (text or "").strip()
		if not content:
			return [""] * max_lines

		lines = []
		for paragraph in content.splitlines():
			paragraph = paragraph.strip()
			if not paragraph:
				lines.append("")
				continue

			wrapped = textwrap.wrap(
				paragraph,
				width=width,
				break_long_words=True,
				break_on_hyphens=False,
			)
			lines.extend(wrapped if wrapped else [""])

		if len(lines) > max_lines:
			overflow = " ".join(lines[max_lines - 1:]).strip()
			lines = lines[:max_lines - 1] + [overflow]

		if len(lines) < max_lines:
			lines.extend([""] * (max_lines - len(lines)))

		return lines

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		sheet_id = kwargs.get("id")
		sheet = get_object_or_404(
			SheetMaintenance.objects.select_related(
				'id_sheet_project__project__partner',
				'responsible_technical',
				'resource_item',
			),
			pk=sheet_id
		)
		context["sheet"] = sheet
		maintenance_lines = self._split_text_lines(
			sheet.maintenance_description,
			width=88,
			max_lines=6,
		)
		fault_lines = self._split_text_lines(
			sheet.fault_description,
			width=48,
			max_lines=6,
		)
		possible_causes_lines = self._split_text_lines(
			sheet.possible_causes,
			width=48,
			max_lines=6,
		)

		context["maintenance_lines"] = maintenance_lines
		context["fault_cause_lines"] = zip(fault_lines, possible_causes_lines)
		return context
