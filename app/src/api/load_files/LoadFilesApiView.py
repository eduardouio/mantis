import os
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from accounts.models.Technical import Technical
from accounts.models.VaccinationRecord import VaccinationRecord
from accounts.models.PassTechnical import PassTechnical
from equipment.models.CertificationVehicle import CertificationVehicle
from equipment.models.PassVehicle import PassVehicle
from equipment.models.Vehicle import Vehicle
from projects.models.CustodyChain import CustodyChain
from projects.models.SheetProject import SheetProject
from projects.models.ShippingGuide import ShippingGuide
from equipment.models.ResourceItem import ResourceItem


# Registro centralizado: modelo → campos de archivo permitidos
MODEL_FILE_REGISTRY = {
    'technical': {
        'model': Technical,
        'fields': ['dni_file', 'license_file', 'vaccine_certificate_file'],
    },
    'vaccination_record': {
        'model': VaccinationRecord,
        'fields': ['vaccine_file'],
    },
    'pass_technical': {
        'model': PassTechnical,
        'fields': ['pass_file'],
    },
    'certification_vehicle': {
        'model': CertificationVehicle,
        'fields': ['certification_file'],
    },
    'pass_vehicle': {
        'model': PassVehicle,
        'fields': ['pass_file'],
    },
    'vehicle': {
        'model': Vehicle,
        'fields': ['vehicle_image', 'poliza_file', 'matricula_file', 'rev_tec_file'],
    },
    'custody_chain': {
        'model': CustodyChain,
        'fields': ['custody_chain_file'],
    },
    'sheet_project': {
        'model': SheetProject,
        'fields': ['sheet_project_file', 'certificate_final_disposition_file', 'invoice_file', 'laboratory_analysis_file'],
    },
    'shipping_guide': {
        'model': ShippingGuide,
        'fields': ['shipping_guide_file'],
    },
    'resource_item': {
        'model': ResourceItem,
        'fields': ['resource_image', 'resource_image_2'],
    },
}


def _get_model_and_instance(model_type, object_id):
    """
    Retorna la configuración del registro y la instancia del modelo.
    Lanza ValueError si el model_type no existe.
    Lanza Http404 si el object_id no corresponde a ningún registro.
    """
    config = MODEL_FILE_REGISTRY.get(model_type)
    if not config:
        raise ValueError(
            f'Tipo de modelo "{model_type}" no válido. '
            f'Opciones: {", ".join(MODEL_FILE_REGISTRY.keys())}'
        )
    instance = get_object_or_404(config['model'], pk=object_id)
    return config, instance


def _validate_field(config, field_name, model_type):
    """Verifica que el field_name sea un campo de archivo permitido."""
    if field_name not in config['fields']:
        raise ValueError(
            f'Campo "{field_name}" no permitido para "{model_type}". '
            f'Campos válidos: {", ".join(config["fields"])}'
        )


@method_decorator(csrf_exempt, name='dispatch')
class LoadFilesApiView(View):
    """
    API centralizada para gestión de archivos en los modelos del sistema.

    POST   → Subir o reemplazar un archivo
    DELETE → Eliminar un archivo existente
    GET    → Consultar información del archivo de un registro

    Parámetros comunes (form-data para POST, query params para GET/DELETE):
        - model_type:  clave del modelo (technical, vehicle, etc.)
        - object_id:   PK del registro
        - field_name:  nombre del campo FileField/ImageField
        - file:        archivo a subir (solo POST)
    """

    # ------------------------------------------------------------------ POST
    def post(self, request):
        """Subir o reemplazar un archivo en un modelo."""
        try:
            model_type = request.POST.get('model_type', '').strip().lower()
            object_id = request.POST.get('object_id')
            field_name = request.POST.get('field_name', '').strip()
            uploaded_file = request.FILES.get('file')

            # Validaciones básicas
            if not all([model_type, object_id, field_name]):
                return JsonResponse({
                    'success': False,
                    'error': 'Se requieren los campos: model_type, object_id, field_name',
                }, status=400)

            if not uploaded_file:
                return JsonResponse({
                    'success': False,
                    'error': 'No se envió ningún archivo (campo "file").',
                }, status=400)

            config, instance = _get_model_and_instance(model_type, object_id)
            _validate_field(config, field_name, model_type)

            # Validar planilla cerrada: solo se pueden agregar archivos nuevos, no reemplazar ni eliminar
            if model_type == 'sheet_project' and hasattr(instance, 'is_closed') and instance.is_closed:
                old_field = getattr(instance, field_name)
                if old_field and old_field.name:
                    return JsonResponse({
                        'success': False,
                        'error': 'No se puede modificar archivos de una planilla cerrada. '
                                 'Solo se pueden agregar archivos en campos vacíos.',
                    }, status=400)

            # Validar cadena de custodia con planilla cerrada
            if model_type == 'custody_chain' and hasattr(instance, 'sheet_project'):
                if instance.sheet_project and instance.sheet_project.is_closed:
                    old_field = getattr(instance, field_name)
                    if old_field and old_field.name:
                        return JsonResponse({
                            'success': False,
                            'error': 'No se puede modificar archivos de una cadena de custodia '
                                     'con planilla cerrada. Solo se pueden agregar archivos en campos vacíos.',
                        }, status=400)

            # Eliminar archivo anterior si existe
            old_field = getattr(instance, field_name)
            if old_field and old_field.name:
                try:
                    old_field.delete(save=False)
                except Exception:
                    pass  # si no puede borrar el anterior, continúa

            # Asignar el nuevo archivo y guardar
            setattr(instance, field_name, uploaded_file)
            update_fields = [field_name]

            # Lógica especial para factura: actualizar referencia y estado
            if model_type == 'sheet_project' and field_name == 'invoice_file':
                invoice_reference = request.POST.get('invoice_reference', '').strip()
                if invoice_reference:
                    instance.invoice_reference = invoice_reference
                    update_fields.append('invoice_reference')
                instance.status = 'INVOICED'
                update_fields.append('status')

            instance.save(update_fields=update_fields)

            new_field = getattr(instance, field_name)
            return JsonResponse({
                'success': True,
                'message': f'Archivo subido correctamente al campo "{field_name}".',
                'data': {
                    'model_type': model_type,
                    'object_id': int(object_id),
                    'field_name': field_name,
                    'file_name': os.path.basename(new_field.name) if new_field else None,
                    'file_url': new_field.url if new_field else None,
                },
            })

        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    # ---------------------------------------------------------------- DELETE
    def delete(self, request):
        """Eliminar un archivo de un registro."""
        try:
            model_type = request.GET.get('model_type', '').strip().lower()
            object_id = request.GET.get('object_id')
            field_name = request.GET.get('field_name', '').strip()

            if not all([model_type, object_id, field_name]):
                return JsonResponse({
                    'success': False,
                    'error': 'Se requieren los parámetros: model_type, object_id, field_name',
                }, status=400)

            config, instance = _get_model_and_instance(model_type, object_id)
            _validate_field(config, field_name, model_type)

            # Validar planilla cerrada: no se pueden eliminar archivos
            if model_type == 'sheet_project' and hasattr(instance, 'is_closed') and instance.is_closed:
                return JsonResponse({
                    'success': False,
                    'error': 'No se puede eliminar archivos de una planilla cerrada.',
                }, status=400)

            # Validar cadena de custodia con planilla cerrada
            if model_type == 'custody_chain' and hasattr(instance, 'sheet_project'):
                if instance.sheet_project and instance.sheet_project.is_closed:
                    return JsonResponse({
                        'success': False,
                        'error': 'No se puede eliminar archivos de una cadena de custodia con planilla cerrada.',
                    }, status=400)

            file_field = getattr(instance, field_name)
            if not file_field or not file_field.name:
                return JsonResponse({
                    'success': False,
                    'error': f'El campo "{field_name}" no tiene archivo asignado.',
                }, status=404)

            file_field.delete(save=False)
            setattr(instance, field_name, None)
            instance.save(update_fields=[field_name])

            return JsonResponse({
                'success': True,
                'message': f'Archivo eliminado del campo "{field_name}".',
                'data': {
                    'model_type': model_type,
                    'object_id': int(object_id),
                    'field_name': field_name,
                },
            })

        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    # ------------------------------------------------------------------ GET
    def get(self, request):
        """Consultar la información del archivo de un registro."""
        try:
            model_type = request.GET.get('model_type', '').strip().lower()
            object_id = request.GET.get('object_id')
            field_name = request.GET.get('field_name', '').strip()

            if not all([model_type, object_id, field_name]):
                return JsonResponse({
                    'success': False,
                    'error': 'Se requieren los parámetros: model_type, object_id, field_name',
                }, status=400)

            config, instance = _get_model_and_instance(model_type, object_id)
            _validate_field(config, field_name, model_type)

            file_field = getattr(instance, field_name)
            has_file = bool(file_field and file_field.name)

            data = {
                'model_type': model_type,
                'object_id': int(object_id),
                'field_name': field_name,
                'has_file': has_file,
                'file_name': os.path.basename(file_field.name) if has_file else None,
                'file_url': file_field.url if has_file else None,
            }

            return JsonResponse({'success': True, 'data': data})

        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ModelFileFieldsApiView(View):
    """
    API auxiliar para consultar los campos de archivo disponibles
    por tipo de modelo. Útil para el frontend.

    GET /api/load_files/fields/?model_type=technical
    GET /api/load_files/fields/  (sin params → todos los modelos)
    """

    def get(self, request):
        model_type = request.GET.get('model_type', '').strip().lower()

        if model_type:
            config = MODEL_FILE_REGISTRY.get(model_type)
            if not config:
                return JsonResponse({
                    'success': False,
                    'error': f'Tipo de modelo "{model_type}" no válido.',
                }, status=400)
            return JsonResponse({
                'success': True,
                'data': {
                    'model_type': model_type,
                    'fields': config['fields'],
                },
            })

        # Retornar todos los modelos y sus campos
        result = {
            key: conf['fields']
            for key, conf in MODEL_FILE_REGISTRY.items()
        }
        return JsonResponse({'success': True, 'data': result})
