from django.views.generic import TemplateView


class WorkSheetTemplateView(TemplateView):
	template_name = "reports/worksheet_template.html"