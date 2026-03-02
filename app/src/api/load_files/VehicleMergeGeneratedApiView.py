"""
API para generar y combinar los PDFs de un vehículo en un solo documento.

GET /api/load_files/vehicle/<vehicle_id>/merge-generated/

Orden de los documentos:
    1. Reporte de estado del vehículo (generado por el sistema)
    2. Póliza de Seguro (adjunta)
    3. Matrícula (adjunta)
    4. Revisión Técnica (adjunta)
    5. Certificaciones técnicas (adjuntas)
    6. Pases de bloques (adjuntos)
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

from equipment.models import Vehicle, PassVehicle, CertificationVehicle


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


def _generate_vehicle_merge_in_thread(cookies, vehicle_id, vehicle_plate,
                                       poliza_path, matricula_path,
                                       rev_tec_path, certification_paths,
                                       pass_paths):
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

        # 1. Reporte de estado del vehículo (generado, portrait)
        try:
            url = f"{settings.BASE_URL}{reverse('vehicle-status-report', kwargs={'pk': vehicle_id})}"
            pdf_bytes = _render_url_to_pdf(page, url)
            _add_pdf_bytes_to_writer(writer, pdf_bytes)
            docs_added += 1
        except Exception:
            pass

        browser.close()

    # 2. Póliza de Seguro (archivo adjunto)
    if _add_file_to_writer(writer, poliza_path):
        docs_added += 1

    # 3. Matrícula (archivo adjunto)
    if _add_file_to_writer(writer, matricula_path):
        docs_added += 1

    # 4. Revisión Técnica (archivo adjunto)
    if _add_file_to_writer(writer, rev_tec_path):
        docs_added += 1

    # 5. Certificaciones técnicas (archivos adjuntos)
    for cert_path in certification_paths:
        if _add_file_to_writer(writer, cert_path):
            docs_added += 1

    # 6. Pases de bloques (archivos adjuntos)
    for pass_path in pass_paths:
        if _add_file_to_writer(writer, pass_path):
            docs_added += 1

    if docs_added == 0:
        return None

    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


@method_decorator(csrf_exempt, name='dispatch')
class VehicleMergeGeneratedApiView(View):
    """
    Genera un PDF combinado con todos los documentos de un vehículo.

    Orden:
        1. Reporte de estado del vehículo (generado)
        2. Póliza de Seguro (adjunta)
        3. Matrícula (adjunta)
        4. Revisión Técnica (adjunta)
        5. Certificaciones técnicas (adjuntas)
        6. Pases de bloques (adjuntos)
    """

    def _get_file_path(self, file_field):
        """Obtiene la ruta del archivo si existe."""
        if file_field and file_field.name:
            try:
                return file_field.path
            except Exception:
                pass
        return None

    def get(self, request, vehicle_id):
        try:
            vehicle = get_object_or_404(Vehicle, pk=vehicle_id, is_active=True)

            cookies = _get_cookies(request)

            # Obtener rutas de archivos adjuntos del vehículo
            poliza_path = self._get_file_path(vehicle.poliza_file)
            matricula_path = self._get_file_path(vehicle.matricula_file)
            rev_tec_path = self._get_file_path(vehicle.rev_tec_file)

            # Obtener rutas de certificaciones
            certifications = CertificationVehicle.objects.filter(
                vehicle=vehicle, is_active=True
            ).order_by('name')
            certification_paths = [
                self._get_file_path(cert.certification_file)
                for cert in certifications
            ]

            # Obtener rutas de pases
            passes = PassVehicle.get_by_vehicle(vehicle.id)
            pass_paths = [
                self._get_file_path(p.pass_file)
                for p in passes
            ]

            # Ejecutar Playwright en un hilo separado
            from datetime import datetime

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    _generate_vehicle_merge_in_thread,
                    cookies,
                    vehicle.id,
                    vehicle.no_plate,
                    poliza_path,
                    matricula_path,
                    rev_tec_path,
                    certification_paths,
                    pass_paths,
                )
                merged_bytes = future.result(timeout=120)

            if merged_bytes is None:
                return JsonResponse({
                    'success': False,
                    'error': 'No se pudo generar ningún documento para este vehículo.',
                }, status=404)

            filename = (
                f"Documentos-Vehiculo-{vehicle.no_plate}-"
                f"{datetime.now().strftime('%Y%m%d')}.pdf"
            )

            response = HttpResponse(merged_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Http404:
            return JsonResponse({'success': False, 'error': 'Vehículo no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
