from django.views.generic import TemplateView
from common.AppLoggin import loggin_event
from projects.models.CustodyChain import CustodyChain
from projects.models.SheetProject import SheetProject
from projects.models.Project import ProjectResourceItem


class FinalDispositionCertificateView(TemplateView):
    template_name = "reports/final_disposition_certificate.html"

    def get_context_data(self, **kwargs):
        loggin_event("Mostrando certificado de disposición final")
        context = super().get_context_data(**kwargs)

        # Datos de ejemplo para visualizar el formato
        context.update(
            {
                "certificate": {
                    "reference_number": "242PSL-CDF-20250731-00305",
                },
                "partner": {
                    "name": "BIOREMEDIACION BIOX CIA. LTDA",
                    "ruc": "1791856031001",
                },
                "project": {
                    "name": "RÍO LOCO",
                    "location": "CAPE 100",
                },
                "details": [
                    {
                        "date": "2025-07-06",
                        "residue_description": "AGUAS NEGRAS Y GRISES",
                        "custody_chain_number": "11838",
                        "treatment_type": "TB3",
                        "barrels": 3.10,
                        "cubic_meters": 0.49,
                    },
                    {
                        "date": "2025-07-11",
                        "residue_description": "AGUAS NEGRAS Y GRISES",
                        "custody_chain_number": "11847",
                        "treatment_type": "TB3",
                        "barrels": 2.38,
                        "cubic_meters": 0.38,
                    },
                    {
                        "date": "2025-07-19",
                        "residue_description": "AGUAS NEGRAS Y GRISES",
                        "custody_chain_number": "11856",
                        "treatment_type": "TB4",
                        "barrels": 3.10,
                        "cubic_meters": 0.49,
                    },
                    {
                        "date": "2025-07-21",
                        "residue_description": "AGUAS NEGRAS Y GRISES",
                        "custody_chain_number": "12306",
                        "treatment_type": "TB5",
                        "barrels": 2.14,
                        "cubic_meters": 0.34,
                    },
                    {
                        "date": "2025-07-23",
                        "residue_description": "AGUAS NEGRAS Y GRISES",
                        "custody_chain_number": "11859",
                        "treatment_type": "TB6",
                        "barrels": 2.38,
                        "cubic_meters": 0.38,
                    },
                    {
                        "date": "2025-07-26",
                        "residue_description": "AGUAS NEGRAS Y GRISES",
                        "custody_chain_number": "12312",
                        "treatment_type": "TB6",
                        "barrels": 2.38,
                        "cubic_meters": 0.38,
                    },
                    {
                        "date": "2025-07-29",
                        "residue_description": "AGUAS NEGRAS Y GRISES",
                        "custody_chain_number": "12026",
                        "treatment_type": "TB6",
                        "barrels": 2.86,
                        "cubic_meters": 0.45,
                    },
                    {
                        "date": "2025-07-30",
                        "residue_description": "AGUAS NEGRAS Y GRISES",
                        "custody_chain_number": "12727",
                        "treatment_type": "TB6",
                        "barrels": 2.38,
                        "cubic_meters": 0.38,
                    },
                ],
                "total_barrels": 20.71,
                "total_cubic_meters": 3.29,
            }
        )

        return context
