from multiprocessing import context
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from common.AppLoggin import loggin_event



class CustodyChainReportView(TemplateView):
    template_name = "reports/chain_custody.html"

    def get_context_data(self, **kwargs):
        loggin_event("Mostrando cadena de custodia")
        context = super().get_context_data(**kwargs)

        id_custody_chain = kwargs.get("id_custody_chain")
        custody_chain = get_object_or_404(CustodyChain, id=id_custody_chain)

        # Usar get_by_custody_chain en lugar de get_by_sheet_project
        custody_details = ChainCustodyDetail.get_by_custody_chain(
            custody_chain=custody_chain
        )

        if custody_details is None:
            custody_details = []

        custody_details = custody_details.select_related(
            "project_resource__resource_item", "project_resource__project__partner"
        )

        sheet_project = custody_chain.sheet_project
        project = sheet_project.project if sheet_project else None
        partner = project.partner if project else None

        time_duration_hours = None
        if custody_chain.time_duration:
            time_duration_hours = round(float(custody_chain.time_duration) / 60, 2)

        context.update(
            {
                "custody_chain": custody_chain,
                "custody_details": custody_details,
                "sheet_project": sheet_project,
                "project": project,
                "partner": partner,
                "technical": custody_chain.technical,
                "vehicle": custody_chain.vehicle,
                "time_duration_hours": time_duration_hours,
            }
        )

        return context
