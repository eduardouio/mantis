from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from accounts.models.Technical import Technical
from datetime import datetime


class PDFTechnicalVaccineReport(View):
    def render_pdf_to_bytes(self, url):
        """Renderiza la página con Playwright y devuelve el PDF como bytes."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(ignore_https_errors=True)
            page.goto(url)

            page.wait_for_load_state("networkidle")

            pdf_bytes = page.pdf(
                format="A4",
                margin={
                    "top": "0.5cm",
                    "right": "0.5cm",
                    "bottom": "0.5cm",
                    "left": "0.5cm",
                },
                print_background=True,
            )
            browser.close()
            return pdf_bytes

    def get(self, request, id, *args, **kwargs):
        """Genera un PDF del reporte de vacunas del técnico y lo devuelve como respuesta."""
        vaccine_report_path = reverse(
            "reports:technical-vaccine-report",
            kwargs={"id": id},
        )
        target_url = request.build_absolute_uri(vaccine_report_path)

        pdf_bytes = self.render_pdf_to_bytes(target_url)

        try:
            technical = Technical.objects.get(id=id)
            filename = (
                f"ReporteVacunas-{technical.dni}-"
                f"{technical.first_name.replace(' ', '')}{technical.last_name.replace(' ', '')}-"
                f'{datetime.now().strftime("%Y%m%d")}.pdf'
            )
        except Technical.DoesNotExist:
            filename = f"ReporteVacunas-{id}-{datetime.now().strftime('%Y%m%d')}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response