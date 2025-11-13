from django.views.generic import TemplateView


class CustodyChainReportView(TemplateView):
	template_name = "reports/chain_custody.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['id_custody_chain'] = kwargs.get('id_custody_chain')
		return context