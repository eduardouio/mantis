from django.views.generic import TemplateView


class CustodyChainReportView(TemplateView):
	template_name = "reports/chain_custody.html"
