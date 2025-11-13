from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from projects.models.CustodyChain import CustodyChain
from django.conf import settings
from datetime import datetime


class PDFCustodyChain(View):
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

    def get(self, request, id_custody_chain, *args, **kwargs):
        """Genera un PDF de la cadena de custodia y lo devuelve como respuesta."""
        custody_chain_path = reverse(
            "reports:custody-chain-report",
            kwargs={"id_custody_chain": id_custody_chain},
        )
        target_url = request.build_absolute_uri(custody_chain_path)

        pdf_bytes = self.render_pdf_to_bytes(target_url)

        try:
            custody_chain = CustodyChain.objects.get(id=id_custody_chain)
            filename = (
                f"CadenaCustodia-{custody_chain.consecutive or id_custody_chain}-"
                f'{custody_chain.created_at.strftime("%Y%m%d")}.pdf'
            )
        except CustodyChain.DoesNotExist:

            filename = f"CadenaCustodia-{id_custody_chain}-{datetime.now().strftime('%Y%m%d')}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
