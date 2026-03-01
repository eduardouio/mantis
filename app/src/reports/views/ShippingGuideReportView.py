from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.ShippingGuide import ShippingGuide, ShippingGuideDetail


class ShippingGuideReportView(TemplateView):
	template_name = "reports/shipping_guide.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		shipping_guide_id = kwargs.get("id")
		guide = get_object_or_404(
			ShippingGuide.objects.select_related('project__partner'),
			pk=shipping_guide_id
		)
		details = ShippingGuideDetail.objects.filter(
			shipping_guide=guide
		).select_related('id_resource_item').order_by('id')

		# Rellenar filas vacías para mantener el formato del reporte
		details_list = list(details)
		min_rows = 11
		empty_rows = max(0, min_rows - len(details_list))

		context["guide"] = guide
		context["details"] = details_list
		context["empty_rows"] = range(empty_rows)
		return context