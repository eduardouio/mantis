from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from equipment.models.ResourceItem import ResourceItem
from datetime import datetime
from django.conf import settings


class PDFBathroomCamperChecker(View):
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

    def get(self, request, equipment_id, *args, **kwargs):
        """Genera un PDF del checklist de camper baño."""
        template_path = reverse(
            "equipment-bathroom-camper-checklist",
            kwargs={"equipment_id": equipment_id},
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
            equipment = ResourceItem.objects.get(id=equipment_id)
            filename = (
                f"Checklist-CamperBano-{equipment.code}-"
                f'{datetime.now().strftime("%Y%m%d")}.pdf'
            )
        except ResourceItem.DoesNotExist:
            filename = f"Checklist-CamperBano-{equipment_id}-{datetime.now().strftime('%Y%m%d')}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
