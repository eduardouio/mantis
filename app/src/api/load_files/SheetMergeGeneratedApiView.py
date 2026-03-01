"""
API para generar y combinar los PDFs de una planilla en un solo documento.

GET /api/load_files/sheet/<sheet_id>/merge-generated/

Orden de los documentos:
    1. Planilla de cantidades (generada por el sistema)
    2. Certificado de disposición final (generado por el sistema)
    3. Factura de venta (adjuntada a la planilla)
    4. Cadenas de custodia (generadas por el sistema)
"""

import io
import os

from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.urls import reverse

from playwright.sync_api import sync_playwright
from pypdf import PdfWriter, PdfReader

from projects.models.SheetProject import SheetProject
from projects.models.CustodyChain import CustodyChain


def _get_cookies(request):
    """Extrae las cookies del request para pasarlas a Playwright."""
    domain = settings.BASE_URL.split("://")[1].split(":")[0]
    return [
        {"name": name, "value": value, "domain": domain, "path": "/"}
        for name, value in request.COOKIES.items()
    ]


def _render_url_to_pdf(page, url, landscape=False, margin=None):
    """Navega a una URL y genera el PDF como bytes."""
    if margin is None:
        margin = {"top": "0.5cm", "right": "0.5cm", "bottom": "0.5cm", "left": "0.5cm"}

    page.goto(url)
    page.wait_for_load_state("networkidle")

    return page.pdf(
        format="A4",
        landscape=landscape,
        margin=margin,
        print_background=True,
    )


def _add_pdf_bytes_to_writer(writer, pdf_bytes):
    """Agrega las páginas de un PDF (bytes) al PdfWriter."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    for p in reader.pages:
        writer.add_page(p)


def _add_file_to_writer(writer, file_field):
    """Agrega un archivo FileField al PdfWriter si existe."""
    if file_field and file_field.name:
        try:
            path = file_field.path
            if os.path.isfile(path):
                reader = PdfReader(path)
                for p in reader.pages:
                    writer.add_page(p)
                return True
        except Exception:
            pass
    return False


@method_decorator(csrf_exempt, name='dispatch')
class SheetMergeGeneratedApiView(View):
    """
    Genera un PDF combinado con todos los documentos de una planilla.

    Orden:
        1. Planilla de cantidades (generada)
        2. Certificado de disposición final (generado)
        3. Factura de venta (adjunta)
        4. Cadenas de custodia (generadas)
    """

    def get(self, request, sheet_id):
        try:
            sheet = get_object_or_404(
                SheetProject.objects.select_related('project', 'project__partner'),
                pk=sheet_id,
                is_active=True,
            )

            cookies = _get_cookies(request)
            writer = PdfWriter()
            docs_added = 0

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(ignore_https_errors=True)
                if cookies:
                    context.add_cookies(cookies)
                page = context.new_page()

                # 1. Planilla de cantidades (generada, landscape)
                try:
                    url = f"{settings.BASE_URL}{reverse('worksheet-template', kwargs={'id': sheet.id})}"
                    pdf_bytes = _render_url_to_pdf(page, url, landscape=True)
                    _add_pdf_bytes_to_writer(writer, pdf_bytes)
                    docs_added += 1
                except Exception:
                    pass

                # 2. Certificado de disposición final (generado, portrait)
                try:
                    url = f"{settings.BASE_URL}{reverse('final-disposition-certificate', kwargs={'id': sheet.id})}"
                    margin = {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}
                    pdf_bytes = _render_url_to_pdf(page, url, landscape=False, margin=margin)
                    _add_pdf_bytes_to_writer(writer, pdf_bytes)
                    docs_added += 1
                except Exception:
                    pass

                # 3. Factura de venta (archivo adjunto)
                if _add_file_to_writer(writer, sheet.invoice_file):
                    docs_added += 1

                # 4. Cadenas de custodia (generadas)
                chains = CustodyChain.objects.filter(
                    sheet_project=sheet,
                    is_active=True,
                ).order_by('activity_date', 'consecutive')

                for chain in chains:
                    try:
                        url = f"{settings.BASE_URL}{reverse('custody-chain-report', kwargs={'id_custody_chain': chain.id})}"
                        pdf_bytes = _render_url_to_pdf(page, url)
                        _add_pdf_bytes_to_writer(writer, pdf_bytes)
                        docs_added += 1
                    except Exception:
                        continue

                browser.close()

            if docs_added == 0:
                return JsonResponse({
                    'success': False,
                    'error': 'No se pudo generar ningún documento para esta planilla.',
                }, status=404)

            buffer = io.BytesIO()
            writer.write(buffer)
            merged_bytes = buffer.getvalue()

            partner_name = sheet.project.partner.name if sheet.project and sheet.project.partner else f'Proyecto_{sheet.project_id}'
            safe_name = partner_name.replace(' ', '_')[:40]
            filename = f"Merge_{sheet.series_code}_{safe_name}.pdf"

            response = HttpResponse(merged_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Http404:
            return JsonResponse({'success': False, 'error': 'Planilla no encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
