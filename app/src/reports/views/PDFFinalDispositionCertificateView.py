import os

from datetime import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View
from weasyprint import HTML

from reports.views.FinalDispositionCertificate import FinalDispositionCertificateView


class PDFFinalDispositionCertificateView(View):
    def _build_context(self, request, sheet_project_id):
        """Reutiliza la lógica de FinalDispositionCertificateView para obtener el contexto."""
        view = FinalDispositionCertificateView()
        view.request = request
        view.kwargs = {"id": sheet_project_id}
        return view.get_context_data()

    def get(self, request, *args, **kwargs):
        """Genera un PDF del certificado de disposición final con WeasyPrint."""
        sheet_project_id = kwargs.get('id')

        context = self._build_context(request, sheet_project_id)
        html_string = render_to_string(
            "reports/final_disposition_certificate.html", context, request=request
        )

        base_url = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "static",
        )
        pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()

        filename = f"CertificadoDisposicionFinal-{sheet_project_id}-{datetime.now().strftime('%Y%m%d')}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
