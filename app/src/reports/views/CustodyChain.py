import math
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from projects.models.CustodyChain import CustodyChain, ChainCustodyDetail
from common.AppLoggin import loggin_event

CUSTODY_ROWS_PER_PAGE = 9


class CustodyChainReportView(TemplateView):
    template_name = "reports/chain_custody.html"

    def get_context_data(self, **kwargs):
        loggin_event("Mostrando cadena de custodia")
        context = super().get_context_data(**kwargs)

        id_custody_chain = kwargs.get("id_custody_chain")
        custody_chain = get_object_or_404(CustodyChain, id=id_custody_chain)

        custody_details = ChainCustodyDetail.get_by_custody_chain(
            custody_chain=custody_chain
        )

        if custody_details is None:
            custody_details = []

        custody_details = custody_details.select_related(
            "project_resource__resource_item", "project_resource__project__partner"
        )

        custody_details_list = list(custody_details)

        sheet_project = custody_chain.sheet_project
        project = sheet_project.project if sheet_project else None
        partner = project.partner if project else None

        time_duration_hours = None
        if custody_chain.time_duration:
            time_duration_hours = round(float(custody_chain.time_duration) / 60, 2)

        # Paginar detalles en bloques de 10
        total_pages = max(1, math.ceil(len(custody_details_list) / CUSTODY_ROWS_PER_PAGE))
        pages = []
        for i in range(total_pages):
            start = i * CUSTODY_ROWS_PER_PAGE
            chunk = custody_details_list[start:start + CUSTODY_ROWS_PER_PAGE]
            empty_rows = CUSTODY_ROWS_PER_PAGE - len(chunk)
            pages.append({
                'details': chunk,
                'empty_rows': range(empty_rows),
                'page_number': i + 1,
                'is_first': i == 0,
                'detail_count': len(chunk),
            })

        consecutive_formatted = '00000000'
        if custody_chain.consecutive:
            consecutive_formatted = str(custody_chain.consecutive).zfill(8)

        context.update(
            {
                "custody_chain": custody_chain,
                "pages": pages,
                "total_pages": total_pages,
                "sheet_project": sheet_project,
                "project": project,
                "partner": partner,
                "technical": custody_chain.technical,
                "vehicle": custody_chain.vehicle,
                "time_duration_hours": time_duration_hours,
                "consecutive_formatted": consecutive_formatted,
            }
        )

        # Datos de firma del usuario
        if self.request.user.is_authenticated:
            context['siganture_name'] = self.request.user.siganture_name or ''
            context['siganture_role'] = self.request.user.siganture_role or ''

        return context
