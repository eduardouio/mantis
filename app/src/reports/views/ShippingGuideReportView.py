import math
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.ShippingGuide import ShippingGuide, ShippingGuideDetail

ROWS_PER_PAGE = 11


class ShippingGuideReportView(TemplateView):
	template_name = "reports/shipping_guide.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		shipping_guide_id = kwargs.get("id")
		guide = get_object_or_404(
			ShippingGuide.objects.select_related('project__partner'),
			pk=shipping_guide_id
		)
		details = list(
			ShippingGuideDetail.objects.filter(
				shipping_guide=guide
			).select_related('id_resource_item').order_by('id')
		)

		# Paginar detalles en bloques de 11
		total_pages = max(1, math.ceil(len(details) / ROWS_PER_PAGE))
		pages = []
		for i in range(total_pages):
			start = i * ROWS_PER_PAGE
			chunk = details[start:start + ROWS_PER_PAGE]
			empty_rows = ROWS_PER_PAGE - len(chunk)
			pages.append({
				'details': chunk,
				'empty_rows': range(empty_rows),
				'page_number': i + 1,
				'item_offset': start,
			})

		context["guide"] = guide
		context["guide_origin_place"] = guide.get_effective_origin_place()
		context["guide_destination_place"] = guide.get_effective_destination_place()
		context["pages"] = pages
		context["total_pages"] = total_pages
		return context