from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from django.conf import settings
from datetime import datetime


class PDFFinalDispositionCertificateView(View):
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
                landscape=False,  # Vertical (portrait)
                margin={
                    "top": "1cm",
                    "right": "1cm",
                    "bottom": "1cm",
                    "left": "1cm",
                },
                print_background=True,
            )
            browser.close()
            return pdf_bytes

    def get(self, request, *args, **kwargs):
        """Genera un PDF del certificado de disposición final y lo devuelve como respuesta."""
        # Obtener el ID del worksheet desde los parámetros de URL
        sheet_project_id = kwargs.get('id')
        
        certificate_path = reverse("final-disposition-certificate", kwargs={'id': sheet_project_id})
        target_url = f"{settings.BASE_URL}{certificate_path}"

        cookies = []
        for name, value in request.COOKIES.items():
            cookies.append(
                {
                    "name": name,
                    "value": value,
                    "domain": settings.BASE_URL.split("://")[1].split(":")[0],
                    "path": "/",
                }
            )

        pdf_bytes = self.render_pdf_to_bytes(target_url, cookies)

        filename = f"CertificadoDisposicionFinal-{sheet_project_id}-{datetime.now().strftime('%Y%m%d')}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
