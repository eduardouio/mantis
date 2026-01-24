from django.views.generic import TemplateView
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from common.AppLoggin import loggin_event


# /reports/
class CustodyChainReportView(TemplateView):
	template_name = "reports/chain_custody.html"

	def get_context_data(self, **kwargs):
		loggin_event(
			'Mosrando cadena de custodia'
		)
		context = super().get_context_data(**kwargs)
		context['id_custody_chain'] = kwargs.get('id_custody_chain')
		return context