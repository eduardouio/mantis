"""
API para generar y combinar los PDFs de un técnico en un solo documento.

GET /api/load_files/technical/<technical_id>/merge-generated/

Orden de los documentos:
    1. Reporte general del técnico (generado por el sistema)
    2. Reporte de vacunas (generado por el sistema)
    3. Cédula (adjunta)
    4. Licencia (adjunta)
    5. Certificado de vacunación (adjunto)
    6. Pases técnicos (adjuntos)
    7. Registros de vacunación (adjuntos)
"""

import io
import os
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.urls import reverse

from playwright.sync_api import sync_playwright
from pypdf import PdfWriter, PdfReader

from accounts.models import Technical, PassTechnical, VaccinationRecord


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


def _add_file_to_writer(writer, file_path):
    """Agrega un archivo PDF al PdfWriter si existe en disco."""
    if file_path and os.path.isfile(file_path):
        try:
            reader = PdfReader(file_path)
            for p in reader.pages:
                writer.add_page(p)
            return True
        except Exception:
            pass
    return False


def _generate_technical_merge_in_thread(cookies, technical_id,
                                         dni_path, license_path,
                                         vaccine_cert_path,
                                         pass_paths, vaccination_paths):
    """
    Ejecuta toda la generación de PDFs con Playwright en un hilo separado.
    Retorna los bytes del PDF combinado o None.
    """
    writer = PdfWriter()
    docs_added = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        if cookies:
            context.add_cookies(cookies)
        page = context.new_page()

        # 1. Reporte general del técnico (generado, portrait)
        try:
            url = f"{settings.BASE_URL}{reverse('technical-information-report', kwargs={'id': technical_id})}"
            pdf_bytes = _render_url_to_pdf(page, url)
            _add_pdf_bytes_to_writer(writer, pdf_bytes)
            docs_added += 1
        except Exception:
            pass

        # 2. Reporte de vacunas (generado, portrait)
        try:
            url = f"{settings.BASE_URL}{reverse('technical-vaccine-report', kwargs={'id': technical_id})}"
            pdf_bytes = _render_url_to_pdf(page, url)
            _add_pdf_bytes_to_writer(writer, pdf_bytes)
            docs_added += 1
        except Exception:
            pass

        browser.close()

    # 3. Cédula (archivo adjunto)
    if _add_file_to_writer(writer, dni_path):
        docs_added += 1

    # 4. Licencia (archivo adjunto)
    if _add_file_to_writer(writer, license_path):
        docs_added += 1

    # 5. Certificado de vacunación (archivo adjunto)
    if _add_file_to_writer(writer, vaccine_cert_path):
        docs_added += 1

    # 6. Pases técnicos (archivos adjuntos)
    for pass_path in pass_paths:
        if _add_file_to_writer(writer, pass_path):
            docs_added += 1

    # 7. Registros de vacunación (archivos adjuntos)
    for vacc_path in vaccination_paths:
        if _add_file_to_writer(writer, vacc_path):
            docs_added += 1

    if docs_added == 0:
        return None

    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


@method_decorator(csrf_exempt, name='dispatch')
class TechnicalMergeGeneratedApiView(View):
    """
    Genera un PDF combinado con todos los documentos de un técnico.

    Orden:
        1. Reporte general del técnico (generado)
        2. Reporte de vacunas (generado)
        3. Cédula (adjunta)
        4. Licencia (adjunta)
        5. Certificado de vacunación (adjunto)
        6. Pases técnicos (adjuntos)
        7. Registros de vacunación (adjuntos)
    """

    def _get_file_path(self, file_field):
        """Obtiene la ruta del archivo si existe."""
        if file_field and file_field.name:
            try:
                return file_field.path
            except Exception:
                pass
        return None

    def get(self, request, technical_id):
        try:
            technical = get_object_or_404(Technical, pk=technical_id, is_active=True)

            cookies = _get_cookies(request)

            # Obtener rutas de archivos adjuntos del técnico
            dni_path = self._get_file_path(technical.dni_file)
            license_path = self._get_file_path(technical.license_file)
            vaccine_cert_path = self._get_file_path(technical.vaccine_certificate_file)

            # Obtener rutas de pases técnicos
            passes = PassTechnical.objects.filter(
                technical=technical, is_active=True
            ).order_by('bloque')
            pass_paths = [
                self._get_file_path(p.pass_file)
                for p in passes
            ]

            # Obtener rutas de registros de vacunación
            vaccinations = VaccinationRecord.get_all_by_technical(
                technical_id=technical.id
            )
            vaccination_paths = [
                self._get_file_path(v.vaccine_file)
                for v in vaccinations
            ]

            # Ejecutar Playwright en un hilo separado
            from datetime import datetime

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    _generate_technical_merge_in_thread,
                    cookies,
                    technical.id,
                    dni_path,
                    license_path,
                    vaccine_cert_path,
                    pass_paths,
                    vaccination_paths,
                )
                merged_bytes = future.result(timeout=120)

            if merged_bytes is None:
                return JsonResponse({
                    'success': False,
                    'error': 'No se pudo generar ningún documento para este técnico.',
                }, status=404)

            safe_name = f"{technical.first_name}_{technical.last_name}".replace(' ', '_')[:40]
            filename = (
                f"Documentos-Tecnico-{technical.dni}-{safe_name}-"
                f"{datetime.now().strftime('%Y%m%d')}.pdf"
            )

            response = HttpResponse(merged_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Http404:
            return JsonResponse({'success': False, 'error': 'Técnico no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
