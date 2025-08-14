from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
import json

from equipment.models import ResourceItem
from equipment.forms.ResourceItemForm import ResourceItemForm
from equipment.models.ResourceItem import (
    SERVICES_FIELDS,
    LVMNOS_FIELDS,
    BTSNHM_FIELDS,
    BTSNMJ_FIELDS,
    EST4UR_FIELDS,
    CMPRBN_FIELDS,
    PTRTAP_FIELDS,
    PTRTAR_FIELDS,
)


class ResourceItemCreateUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'forms/resource_item_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = kwargs.get('pk')
        instance = None
        if pk:
            try:
                instance = ResourceItem.objects.get(pk=pk)
            except ResourceItem.DoesNotExist:
                instance = None

        is_update = instance is not None
        context['is_update'] = is_update
        context['equipment'] = instance
        context['title_section'] = (
            'Editar Equipo' if is_update else 'Registrar Nuevo Equipo'
        )
        context['title_page'] = context['title_section']
        form = ResourceItemForm(instance=instance)
        context['form'] = form

    # 1) Preparar mapa tipo -> campos permitidos
    # (intersectado con los del formulario)
        all_form_fields = list(form.fields.keys())
        full_map = {
            'SERVIC': SERVICES_FIELDS,
            'LVMNOS': LVMNOS_FIELDS,
            'BTSNHM': BTSNHM_FIELDS,
            'BTSNMJ': BTSNMJ_FIELDS,
            'EST4UR': EST4UR_FIELDS,
            'CMPRBN': CMPRBN_FIELDS,
            'PTRTAP': PTRTAP_FIELDS,
            'PTRTAR': PTRTAR_FIELDS,
        }
        allowed_map = {
            key: [f for f in fields if f in all_form_fields]
            for key, fields in full_map.items()
        }

        # 2) Entregar el JSON al template para control dinámico en el cliente
        context['type_fields_map_json'] = json.dumps(allowed_map)
        context['initial_type'] = (
            instance.type_equipment if instance else 'SERVIC'
        )

    # 3) Renderizar TODOS los campos (una sola vez)
    # y dejar que el JS oculte/muestre
        mid = (len(all_form_fields) + 1) // 2
        left_names = all_form_fields[:mid]
        right_names = all_form_fields[mid:]

        context['left_fields'] = left_names
        context['right_fields'] = right_names
        context['left_bound_fields'] = [form[name] for name in left_names]
        context['right_bound_fields'] = [form[name] for name in right_names]
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Maneja solicitudes POST para crear/actualizar recursos"""
        pk = kwargs.get('pk')
        instance = None
        if pk:
            try:
                instance = ResourceItem.objects.get(pk=pk)
            except ResourceItem.DoesNotExist:
                instance = None

        try:
            # Crear el formulario con los datos POST
            form = ResourceItemForm(request.POST, instance=instance)

            # Validar el formulario
            if form.is_valid():
                resource = form.save(commit=False)
                
                # Establecer el estado del equipo
                if not instance:
                    # Si es nuevo, siempre "FUNCIONANDO"
                    resource.stst_status_equipment = 'FUNCIONANDO'
                # Si es actualización, mantiene su estado actual
                
                resource.save()

                # Redirigir a la vista de detalle con parámetro de acción
                action = 'updated' if instance else 'created'
                redirect_url = reverse_lazy(
                    'resource_detail', kwargs={'pk': resource.pk}
                )
                return HttpResponseRedirect(f'{redirect_url}?action={action}')
            else:
                # Si hay errores, re-renderizar el formulario con errores
                context = self.get_context_data(**kwargs)
                context['form'] = form
                return render(request, self.template_name, context)

        except Exception as e:
            # En caso de error, mostrar el formulario con el mensaje de error
            context = self.get_context_data(**kwargs)
            context['error'] = f'Error al guardar el recurso: {str(e)}'
            return render(request, self.template_name, context)
