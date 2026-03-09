"""
API que devuelve el árbol completo de documentos del sistema.
Agrupa los registros por categoría y, para los que dependen de proyecto,
construye un árbol jerárquico:  Proyecto → Planilla → Cadena de Custodia.
"""

import os
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from accounts.models.Technical import Technical
from accounts.models.PassTechnical import PassTechnical
from equipment.models.CertificationVehicle import CertificationVehicle
from equipment.models.PassVehicle import PassVehicle
from equipment.models.Vehicle import Vehicle
from equipment.models.ResourceItem import ResourceItem
from projects.models.CustodyChain import CustodyChain
from projects.models.SheetProject import SheetProject
from projects.models.ShippingGuide import ShippingGuide
from projects.models.Project import Project


def _file_info(instance, field_name):
    """Retorna info del archivo o None si no tiene."""
    field = getattr(instance, field_name, None)
    if field and field.name:
        return {
            'file_name': os.path.basename(field.name),
            'file_url': field.url,
        }
    return None


def _build_file_fields(instance, field_names, model_type):
    """Construye la lista de campos de archivo para un registro."""
    files = []
    for fn in field_names:
        info = _file_info(instance, fn)
        files.append({
            'field_name': fn,
            'field_label': instance._meta.get_field(fn).verbose_name,
            'has_file': info is not None,
            'file_name': info['file_name'] if info else None,
            'file_url': info['file_url'] if info else None,
            'model_type': model_type,
            'object_id': instance.pk,
        })
    return files


# ── Etiquetas legibles para los campos ───────────────────────────────
FIELD_LABELS = {
    'image_profile': 'Foto de Perfil',
    'dni_file': 'Cédula',
    'license_file': 'Licencia',
    'vaccine_certificate_file': 'Certificado de Vacunas',
    'pass_file': 'Pase',
    'certification_file': 'Certificación',
    'vehicle_image': 'Imagen del Vehículo',
    'poliza_file': 'Póliza',
    'matricula_file': 'Matrícula',
    'rev_tec_file': 'Revisión Técnica',
    'custody_chain_file': 'Archivo Cadena de Custodia',
    'sheet_project_file': 'Archivo de Planilla',
    'certificate_final_disposition_file': 'Certificado Disposición Final',
    'invoice_file': 'Archivo de Factura',
    'laboratory_analysis_file': 'Análisis de Laboratorio',
    'shipping_guide_file': 'Guía de Remisión',
    'resource_image': 'Imagen del Equipo',
    'resource_image_2': 'Imagen del Equipo 2',
}


@method_decorator(csrf_exempt, name='dispatch')
class DocumentTreeApiView(View):
    """
    GET /api/load_files/tree/

    Devuelve un JSON con la estructura de documentos agrupada por categorías:
    - technicals: Técnicos y sus sub-documentos (pases, vacunas)
    - vehicles: Vehículos y sus sub-documentos (pases, certificaciones)
    - equipment: Equipos (ResourceItem)
    - projects: Árbol de Proyecto → Planilla → Cadena de Custodia + Guías de Remisión
    """

    def get(self, request):
        try:
            data = {
                'technicals': self._build_technicals(),
                'vehicles': self._build_vehicles(),
                'equipment': self._build_equipment(),
                'projects': self._build_projects(),
            }
            return JsonResponse({'success': True, 'data': data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    # ── Técnicos ─────────────────────────────────────────────────────
    def _build_technicals(self):
        technicals = Technical.objects.filter(is_active=True).order_by('last_name', 'first_name')
        result = []
        for t in technicals:
            passes = PassTechnical.objects.filter(technical=t, is_active=True)

            tech_node = {
                'id': t.pk,
                'label': f'{t.last_name} {t.first_name}',
                'dni': t.dni,
                'detail_url': f'/tecnicos/{t.pk}/',
                'files': _build_file_fields(
                    t,
                    ['image_profile', 'dni_file', 'license_file', 'vaccine_certificate_file'],
                    'technical'
                ),
                'children': [],
            }

            for p in passes:
                tech_node['children'].append({
                    'id': p.pk,
                    'label': f'Pase - {p.bloque}' if hasattr(p, 'bloque') and p.bloque else f'Pase #{p.pk}',
                    'type': 'pass_technical',
                    'files': _build_file_fields(p, ['pass_file'], 'pass_technical'),
                })

            result.append(tech_node)
        return result

    # ── Vehículos ────────────────────────────────────────────────────
    def _build_vehicles(self):
        vehicles = Vehicle.objects.filter(is_active=True).order_by('no_plate')
        result = []
        for v in vehicles:
            passes = PassVehicle.objects.filter(vehicle=v, is_active=True)
            certs = CertificationVehicle.objects.filter(vehicle=v, is_active=True)

            veh_node = {
                'id': v.pk,
                'label': f'{v.no_plate} - {v.brand} {v.model or ""}',
                'detail_url': f'/vehiculos/{v.pk}/',
                'files': _build_file_fields(v, ['vehicle_image', 'poliza_file', 'matricula_file', 'rev_tec_file'], 'vehicle'),
                'children': [],
            }

            for p in passes:
                veh_node['children'].append({
                    'id': p.pk,
                    'label': f'Pase - {p.bloque}' if hasattr(p, 'bloque') and p.bloque else f'Pase #{p.pk}',
                    'type': 'pass_vehicle',
                    'files': _build_file_fields(p, ['pass_file'], 'pass_vehicle'),
                })

            for c in certs:
                veh_node['children'].append({
                    'id': c.pk,
                    'label': f'Cert. {c.get_name_display()}' if hasattr(c, 'get_name_display') else f'Cert. #{c.pk}',
                    'type': 'certification_vehicle',
                    'files': _build_file_fields(c, ['certification_file'], 'certification_vehicle'),
                })

            result.append(veh_node)
        return result

    # ── Equipos ──────────────────────────────────────────────────────
    def _build_equipment(self):
        items = ResourceItem.objects.filter(is_active=True).order_by('name')
        result = []
        for item in items:
            result.append({
                'id': item.pk,
                'label': f'{item.name} ({item.code})',
                'detail_url': f'/equipos/{item.pk}/',
                'files': _build_file_fields(item, ['resource_image', 'resource_image_2'], 'resource_item'),
            })
        return result

    # ── Proyectos (árbol jerárquico) ─────────────────────────────────
    def _build_projects(self):
        projects = Project.objects.filter(is_active=True).select_related('partner').order_by('-id')
        result = []

        for proj in projects:
            proj_node = {
                'id': proj.pk,
                'label': f'{proj.partner.name}' if proj.partner else f'Proyecto #{proj.pk}',
                'detail_url': f'/projects/{proj.pk}/',
                'children': [],
            }

            # Planillas
            sheets = SheetProject.objects.filter(
                project=proj, is_active=True
            ).order_by('-period_start')

            for sheet in sheets:
                sheet_node = {
                    'id': sheet.pk,
                    'label': f'Planilla #{sheet.id} ({sheet.period_start} → {sheet.period_end or "actual"})',
                    'type': 'sheet_project',
                    'files': _build_file_fields(
                        sheet,
                        ['sheet_project_file', 'certificate_final_disposition_file', 'invoice_file', 'laboratory_analysis_file'],
                        'sheet_project',
                    ),
                    'children': [],
                }

                # Cadenas de custodia de esta planilla
                chains = CustodyChain.objects.filter(
                    sheet_project=sheet, is_active=True
                ).order_by('-activity_date')

                for chain in chains:
                    sheet_node['children'].append({
                        'id': chain.pk,
                        'label': f'Cadena #{chain.consecutive} - {chain.activity_date}',
                        'type': 'custody_chain',
                        'files': _build_file_fields(chain, ['custody_chain_file'], 'custody_chain'),
                    })

                proj_node['children'].append(sheet_node)

            # Guías de remisión
            guides = ShippingGuide.objects.filter(
                project=proj, is_active=True
            ).order_by('-issue_date')

            for guide in guides:
                proj_node['children'].append({
                    'id': guide.pk,
                    'label': f'Guía #{guide.guide_number} - {guide.issue_date}',
                    'type': 'shipping_guide',
                    'files': _build_file_fields(guide, ['shipping_guide_file'], 'shipping_guide'),
                })

            result.append(proj_node)

        return result
