from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from common.AppLoggin import loggin_event
from projects.models.CustodyChain import CustodyChain
from projects.models.SheetProject import SheetProject
from projects.models.Project import ProjectResourceItem
from projects.models.Project import Project


class FinalDispositionCertificateView(TemplateView):
    template_name = "reports/final_disposition_certificate.html"

    def get_context_data(self, **kwargs):
        loggin_event("Mostrando certificado de disposición final")
        context = super().get_context_data(**kwargs)

        # Obtener el ID del worksheet desde los parámetros de URL
        sheet_project_id = self.kwargs.get('id')
        
        if not sheet_project_id:
            # Si no hay ID, retornar datos vacíos
            context.update({
                "certificate": {"reference_number": "242PSL-CDF-00000000-00000"},
                "partner": {"name": "", "ruc": ""},
                "project": {"name": "", "location": ""},
                "details": [],
                "total_barrels": 0,
                "total_cubic_meters": 0,
            })
            return context

        # Obtener el SheetProject
        sheet_project = get_object_or_404(SheetProject, id=sheet_project_id)
        project = sheet_project.project
        partner = project.partner

        # Obtener todas las cadenas de custodia asociadas al worksheet
        custody_chains = CustodyChain.objects.filter(
            sheet_project=sheet_project,
            is_deleted=False
        ).order_by('activity_date')

        # Construir la lista de detalles y calcular totales
        details = []
        total_barrels = 0
        total_cubic_meters = 0

        for chain in custody_chains:
            details.append({
                "date": chain.activity_date,
                "residue_description": "AGUAS NEGRAS Y GRISES",
                "custody_chain_number": chain.consecutive or "",
                "treatment_type": "",  # No está en el modelo, se deja vacío
                "barrels": float(chain.total_barrels),
                "cubic_meters": float(chain.total_cubic_meters),
            })
            total_barrels += float(chain.total_barrels)
            total_cubic_meters += float(chain.total_cubic_meters)

        # Actualizar el contexto con datos reales
        context.update({
            "certificate": {
                "reference_number": "242PSL-CDF-20250731-00305",  # Número quemado
            },
            "partner": {
                "name": partner.name,
                "ruc": partner.business_tax_id,
            },
            "project": {
                "name": partner.name,
                "location": f"{project.location or ''} {project.cardinal_point or ''}".strip(),
            },
            "details": details,
            "total_barrels": round(total_barrels, 2),
            "total_cubic_meters": round(total_cubic_meters, 2),
        })

        return context
