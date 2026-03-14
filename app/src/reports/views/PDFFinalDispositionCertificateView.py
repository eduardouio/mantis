import os

from datetime import datetime
from pathlib import Path

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View
from weasyprint import HTML

from reports.views.FinalDispositionCertificate import FinalDispositionCertificateView

# Directorio raíz del proyecto Django (app/src/)
_APP_SRC = Path(__file__).resolve().parent.parent.parent
_STATIC_DIR = _APP_SRC / "static"


def _url_fetcher(url):
    """Resuelve URLs /static/… a archivos locales para que WeasyPrint cargue imágenes."""
    from weasyprint import default_url_fetcher

    if url.startswith("/static/"):
        local_path = _STATIC_DIR / url[len("/static/"):]
        return default_url_fetcher("file://" + str(local_path))
    return default_url_fetcher(url)


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

        pdf_bytes = HTML(
            string=html_string,
            base_url=str(_STATIC_DIR),
            url_fetcher=_url_fetcher,
        ).write_pdf()

        filename = f"CertificadoDisposicionFinal-{sheet_project_id}-{datetime.now().strftime('%Y%m%d')}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
