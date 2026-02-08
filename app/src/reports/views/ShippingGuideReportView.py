from django.views.generic import TemplateView


class ShippingGuideReportView(TemplateView):
	template_name = "reports/shipping_guide.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		shipping_guide_id = kwargs.get("id")
		context["shipping_guide_id"] = shipping_guide_id
		return context