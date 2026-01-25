from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from accounts.models.Technical import Technical
from datetime import datetime


class PDFTechnicalInformation(View):
    def render_pdf_to_bytes(self, url, cookies=None):
        """Renderiza la página con Playwright y devuelve el PDF como bytes."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)

            if cookies:
                context.add_cookies(cookies)

            page = context.new_page()
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
        """Genera un PDF del reporte técnico y lo devuelve como respuesta."""
        technical_report_path = reverse(
            "reports:technical-information-report",
            kwargs={"id": id},
        )
        target_url = f"{request.scheme}://{request.get_host()}{technical_report_path}"

        cookies = []
        for name, value in request.COOKIES.items():
            cookies.append(
                {
                    "name": name,
                    "value": value,
                    "domain": request.get_host().split(":")[0],
                    "path": "/",
                }
            )

        pdf_bytes = self.render_pdf_to_bytes(target_url, cookies)

        try:
            technical = Technical.objects.get(id=id)
            filename = (
                f"ReporteTecnico-{technical.dni}-"
                f"{technical.first_name.replace(' ', '')}{technical.last_name.replace(' ', '')}-"
                f'{datetime.now().strftime("%Y%m%d")}.pdf'
            )
        except Technical.DoesNotExist:
            filename = f"ReporteTecnico-{id}-{datetime.now().strftime('%Y%m%d')}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
