"""
API para obtener el árbol de documentos de un proyecto específico
y para generar merges de PDFs.

GET  /api/load_files/project/<project_id>/tree/  → árbol de documentos del proyecto
GET  /api/load_files/project/<project_id>/merge/  → descarga merge PDF completo
GET  /api/load_files/project/<project_id>/merge/?scope=custody_chains&sheet_id=XX  → merge solo cadenas
POST /api/load_files/project/<project_id>/bulk_custody/  → carga masiva de cadenas de custodia
"""

import io
import json
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from pypdf import PdfWriter, PdfReader

from projects.models.Project import Project
from projects.models.SheetProject import SheetProject
from projects.models.CustodyChain import CustodyChain
from projects.models.ShippingGuide import ShippingGuide


def _file_info(instance, field_name):
    """Retorna info del archivo o None si no tiene."""
    field = getattr(instance, field_name, None)
    if field and field.name:
        return {
            'file_name': os.path.basename(field.name),
            'file_url': field.url,
            'file_path': field.path,
        }
    return None


def _build_file_entry(instance, field_name, model_type, label=None):
    """Construye un dict con info del archivo."""
    info = _file_info(instance, field_name)
    field_label = label or instance._meta.get_field(field_name).verbose_name
    return {
        'field_name': field_name,
        'field_label': field_label,
        'has_file': info is not None,
        'file_name': info['file_name'] if info else None,
        'file_url': info['file_url'] if info else None,
        'model_type': model_type,
        'object_id': instance.pk,
    }


@method_decorator(csrf_exempt, name='dispatch')
class ProjectDocumentTreeApiView(View):
    """Devuelve el árbol de documentos de un proyecto."""

    def get(self, request, project_id):
        try:
            project = get_object_or_404(Project, pk=project_id)
            data = self._build_tree(project)
            return JsonResponse({'success': True, 'data': data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    def _build_tree(self, project):
        tree = {
            'project': {
                'id': project.pk,
                'label': str(project.partner.name) if project.partner else f'Proyecto #{project.pk}',
                'detail_url': f'/projects/{project.pk}/',
            },
            'sheets': [],
            'shipping_guides': [],
            'stats': {'total': 0, 'loaded': 0},
        }

        # ── Planillas ────────────────────────────────────────────
        sheets = SheetProject.objects.filter(
            project=project, is_active=True
        ).order_by('period_start')

        for sheet in sheets:
            sheet_files = [
                _build_file_entry(sheet, 'sheet_project_file', 'sheet_project'),
                _build_file_entry(sheet, 'certificate_final_disposition_file', 'sheet_project'),
                _build_file_entry(sheet, 'invoice_file', 'sheet_project'),
                _build_file_entry(sheet, 'laboratory_analysis_file', 'sheet_project'),
            ]

            sheet_node = {
                'id': sheet.pk,
                'label': f'Planilla #{sheet.id}',
                'period': f'{sheet.period_start} → {sheet.period_end or "actual"}',
                'type': 'sheet_project',
                'files': sheet_files,
                'custody_chains': [],
            }

            # Cadenas de custodia
            chains = CustodyChain.objects.filter(
                sheet_project=sheet, is_active=True
            ).order_by('activity_date', 'consecutive')

            for chain in chains:
                chain_files = [
                    _build_file_entry(chain, 'custody_chain_file', 'custody_chain'),
                ]
                sheet_node['custody_chains'].append({
                    'id': chain.pk,
                    'label': f'Cadena #{chain.consecutive}',
                    'date': str(chain.activity_date),
                    'type': 'custody_chain',
                    'files': chain_files,
                })

                for f in chain_files:
                    tree['stats']['total'] += 1
                    if f['has_file']:
                        tree['stats']['loaded'] += 1

            for f in sheet_files:
                tree['stats']['total'] += 1
                if f['has_file']:
                    tree['stats']['loaded'] += 1

            tree['sheets'].append(sheet_node)

        # ── Guías de remisión ────────────────────────────────────
        guides = ShippingGuide.objects.filter(
            project=project, is_active=True
        ).order_by('issue_date')

        for guide in guides:
            guide_files = [
                _build_file_entry(guide, 'shipping_guide_file', 'shipping_guide'),
            ]
            tree['shipping_guides'].append({
                'id': guide.pk,
                'label': f'Guía #{guide.guide_number}',
                'date': str(guide.issue_date),
                'type': 'shipping_guide',
                'files': guide_files,
            })
            for f in guide_files:
                tree['stats']['total'] += 1
                if f['has_file']:
                    tree['stats']['loaded'] += 1

        return tree


@method_decorator(csrf_exempt, name='dispatch')
class ProjectDocumentMergeApiView(View):
    """
    Genera un PDF combinado de los documentos de un proyecto.

    Query params:
        scope  = all (defecto) | custody_chains | sheet_files | shipping_guides
        sheet_id = (opcional) filtra cadenas/planillas por esta planilla
    """

    def get(self, request, project_id):
        try:
            project = get_object_or_404(Project, pk=project_id)
            scope = request.GET.get('scope', 'all').strip().lower()
            sheet_id = request.GET.get('sheet_id')

            pdf_paths = self._collect_paths(project, scope, sheet_id)

            if not pdf_paths:
                return JsonResponse({
                    'success': False,
                    'error': 'No hay archivos PDF para combinar en el alcance seleccionado.',
                }, status=404)

            merged_bytes = self._merge_pdfs(pdf_paths)
            partner_name = project.partner.name if project.partner else f'Proyecto_{project.pk}'
            safe_name = partner_name.replace(' ', '_')[:50]
            filename = f'Documentos_{safe_name}_{scope}.pdf'

            response = HttpResponse(merged_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Http404:
            return JsonResponse({'success': False, 'error': 'Proyecto no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    def _collect_paths(self, project, scope, sheet_id):
        """Recopila las rutas de archivo en el orden correcto."""
        paths = []

        sheets_qs = SheetProject.objects.filter(
            project=project, is_active=True
        ).order_by('period_start')

        if sheet_id:
            sheets_qs = sheets_qs.filter(pk=sheet_id)

        if scope in ('all', 'sheet_files'):
            for sheet in sheets_qs:
                self._add_if_exists(paths, sheet, 'sheet_project_file')
                self._add_if_exists(paths, sheet, 'certificate_final_disposition_file')
                self._add_if_exists(paths, sheet, 'invoice_file')
                self._add_if_exists(paths, sheet, 'laboratory_analysis_file')

        if scope in ('all', 'custody_chains'):
            for sheet in sheets_qs:
                chains = CustodyChain.objects.filter(
                    sheet_project=sheet, is_active=True
                ).order_by('activity_date', 'consecutive')
                for chain in chains:
                    self._add_if_exists(paths, chain, 'custody_chain_file')

        if scope in ('all', 'shipping_guides'):
            guides_qs = ShippingGuide.objects.filter(
                project=project, is_active=True
            ).order_by('issue_date')
            for guide in guides_qs:
                self._add_if_exists(paths, guide, 'shipping_guide_file')

        return paths

    def _add_if_exists(self, paths, instance, field_name):
        """Agrega la ruta del archivo si existe."""
        field = getattr(instance, field_name, None)
        if field and field.name:
            try:
                path = field.path
                if os.path.isfile(path):
                    paths.append(path)
            except Exception:
                pass

    def _merge_pdfs(self, pdf_paths):
        """Combina una lista de PDFs en un solo archivo."""
        writer = PdfWriter()

        for path in pdf_paths:
            try:
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                # Si un PDF está corrupto, lo salta pero registra en metadata
                writer.add_metadata({
                    f'/SkippedFile': os.path.basename(path),
                    f'/SkipReason': str(e)[:100],
                })

        buffer = io.BytesIO()
        writer.write(buffer)
        return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════
#  Carga masiva de cadenas de custodia
# ═══════════════════════════════════════════════════════════════════════

@method_decorator(csrf_exempt, name='dispatch')
class BulkCustodyUploadApiView(View):
    """
    POST /api/load_files/project/<project_id>/bulk_custody/

    Recibe un PDF donde cada página corresponde a una cadena de custodia
    seleccionada. Divide el PDF en páginas individuales y las asocia
    a las cadenas en el orden indicado.

    Body (multipart/form-data):
        file       – Archivo PDF con N páginas
        chain_ids  – JSON array con los IDs de cadenas seleccionadas (en orden)

    Validaciones:
        - El PDF debe tener exactamente la misma cantidad de páginas
          que cadenas seleccionadas.
        - Todas las cadenas deben pertenecer al proyecto indicado.
    """

    def post(self, request, project_id):
        try:
            project = get_object_or_404(Project, pk=project_id)

            # ── Validar archivo ──────────────────────────────────
            pdf_file = request.FILES.get('file')
            if not pdf_file:
                return JsonResponse({
                    'success': False,
                    'error': 'No se recibió ningún archivo PDF.',
                }, status=400)

            if not pdf_file.name.lower().endswith('.pdf'):
                return JsonResponse({
                    'success': False,
                    'error': 'El archivo debe ser un PDF.',
                }, status=400)

            # ── Validar chain_ids ────────────────────────────────
            raw_ids = request.POST.get('chain_ids', '[]')
            try:
                chain_ids = json.loads(raw_ids)
                if not isinstance(chain_ids, list) or len(chain_ids) == 0:
                    raise ValueError
                chain_ids = [int(cid) for cid in chain_ids]
            except (json.JSONDecodeError, ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'Debe seleccionar al menos una cadena de custodia.',
                }, status=400)

            # ── Verificar que las cadenas pertenecen al proyecto ─
            chains = CustodyChain.objects.filter(
                pk__in=chain_ids,
                sheet_project__project=project,
                is_active=True,
            )

            found_ids = set(chains.values_list('pk', flat=True))
            missing = [cid for cid in chain_ids if cid not in found_ids]
            if missing:
                return JsonResponse({
                    'success': False,
                    'error': f'Las siguientes cadenas no pertenecen al proyecto o no existen: {missing}',
                }, status=400)

            # ── Leer el PDF y contar páginas ─────────────────────
            try:
                reader = PdfReader(pdf_file)
            except Exception:
                return JsonResponse({
                    'success': False,
                    'error': 'El archivo no es un PDF válido o está corrupto.',
                }, status=400)

            num_pages = len(reader.pages)
            num_chains = len(chain_ids)

            if num_pages != num_chains:
                return JsonResponse({
                    'success': False,
                    'error': (
                        f'El PDF tiene {num_pages} página(s) pero se seleccionaron '
                        f'{num_chains} cadena(s) de custodia. '
                        f'Deben coincidir exactamente.'
                    ),
                }, status=400)

            # ── Obtener nombre del proyecto para el nombre del archivo
            partner_name = (
                project.partner.name if project.partner
                else f'Proyecto_{project.pk}'
            )
            safe_project = partner_name.replace(' ', '_')[:40]

            # ── Mapear chain_id → instancia preservando orden ────
            chain_map = {c.pk: c for c in chains}
            ordered_chains = [chain_map[cid] for cid in chain_ids]

            # ── Dividir y guardar ────────────────────────────────
            saved = []
            errors = []

            for idx, chain in enumerate(ordered_chains):
                try:
                    # Extraer una sola página
                    writer = PdfWriter()
                    writer.add_page(reader.pages[idx])

                    buf = io.BytesIO()
                    writer.write(buf)
                    page_bytes = buf.getvalue()

                    # Nombre: CadenaCustodia_<consecutivo>_<proyecto>.pdf
                    consecutive = chain.consecutive or str(chain.pk)
                    filename = f'CadenaCustodia_{consecutive}_{safe_project}.pdf'

                    # Guardar usando el FileField del modelo
                    chain.custody_chain_file.save(
                        filename,
                        ContentFile(page_bytes),
                        save=True,
                    )

                    saved.append({
                        'chain_id': chain.pk,
                        'consecutive': chain.consecutive,
                        'page': idx + 1,
                        'filename': filename,
                    })
                except Exception as e:
                    errors.append({
                        'chain_id': chain.pk,
                        'consecutive': chain.consecutive,
                        'page': idx + 1,
                        'error': str(e),
                    })

            return JsonResponse({
                'success': len(errors) == 0,
                'saved': len(saved),
                'errors_count': len(errors),
                'details': saved,
                'errors': errors,
                'message': (
                    f'Se asignaron {len(saved)} archivo(s) correctamente.'
                    + (f' {len(errors)} error(es).' if errors else '')
                ),
            })

        except Http404:
            return JsonResponse({
                'success': False, 'error': 'Proyecto no encontrado.'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False, 'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PdfPageCountApiView(View):
    """POST /api/load_files/pdf_page_count/

    Recibe un PDF y retorna la cantidad de páginas.
    Body (multipart/form-data):  file – Archivo PDF
    """

    def post(self, request):
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return JsonResponse(
                {'success': False, 'error': 'No se recibió ningún archivo.'},
                status=400,
            )

        if not pdf_file.name.lower().endswith('.pdf'):
            return JsonResponse(
                {'success': False, 'error': 'El archivo debe ser un PDF.'},
                status=400,
            )

        try:
            reader = PdfReader(pdf_file)
            return JsonResponse({'success': True, 'pages': len(reader.pages)})
        except Exception:
            return JsonResponse(
                {'success': False, 'error': 'El archivo no es un PDF válido o está corrupto.'},
                status=400,
            )
