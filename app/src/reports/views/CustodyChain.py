from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from common.AppLoggin import loggin_event


# /reports/
class CustodyChainReportView(TemplateView):
	template_name = "reports/chain_custody.html"

	def get_context_data(self, **kwargs):
		loggin_event(
			'Mostrando cadena de custodia'
		)
		context = super().get_context_data(**kwargs)
		
		id_custody_chain = kwargs.get('id_custody_chain')
		custody_chain = get_object_or_404(CustodyChain, id=id_custody_chain)
		
		# Obtener detalles de la cadena de custodia
		custody_details = ChainCustodyDetail.objects.filter(
			custody_chain=custody_chain
		).select_related(
			'project_resource__resource_item',
			'project_resource__project__partner'
		)
		
		# Obtener información del proyecto
		sheet_project = custody_chain.sheet_project
		project = sheet_project.project
		partner = project.partner
		
		context.update({
			'custody_chain': custody_chain,
			'custody_details': custody_details,
			'sheet_project': sheet_project,
			'project': project,
			'partner': partner,
			'technical': custody_chain.technical,
			'vehicle': custody_chain.vehicle,
		})
		
		return context