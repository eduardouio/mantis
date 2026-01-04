from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from equipment.models.ResourceItem import ResourceItem
from datetime import datetime


class PDFBathroomCamperChecker(View):
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

    def get(self, request, equipment_id, *args, **kwargs):
        """Genera un PDF del checklist de camper baño."""
        template_path = reverse(
            "reports:equipment-bathroom-camper-checklist",
            kwargs={"equipment_id": equipment_id},
        )
        target_url = request.build_absolute_uri(template_path)

        pdf_bytes = self.render_pdf_to_bytes(target_url)

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
