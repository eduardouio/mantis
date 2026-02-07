from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from equipment.models import Vehicle
from datetime import datetime
from django.conf import settings


class PDFVehicleStatusReport(View):
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

    def get(self, request, pk, *args, **kwargs):
        """Genera un PDF del reporte de estado del vehículo."""
        template_path = reverse(
            "vehicle-status-report",
            kwargs={"pk": pk},
        )
        target_url = f"{settings.BASE_URL}{template_path}"

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

        try:
            vehicle = Vehicle.objects.get(id=pk)
            filename = (
                f"Reporte-Vehiculo-{vehicle.no_plate}-"
                f'{datetime.now().strftime("%Y%m%d")}.pdf'
            )
        except Vehicle.DoesNotExist:
            filename = f"Reporte-Vehiculo-{pk}-{datetime.now().strftime('%Y%m%d')}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
