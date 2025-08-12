from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import models
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

from equipment.models import ResourceItem
from equipment.forms.ResourceItemForm import ResourceItemForm


@method_decorator(csrf_exempt, name='dispatch')
class ResourceItemUpdateView(LoginRequiredMixin, UpdateView):
    model = ResourceItem
    template_name = 'forms/resource_item_form.html'
    form_class = ResourceItemForm
    success_url = '/equipos/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Equipo {}'.format(
            self.object.code
        )
        context['title_page'] = 'Actualizar Equipo {}'.format(
            self.object.code
        )
        # Añadir indicadores para el modo de edición
        context['is_update'] = True
        context['equipment'] = self.object

        # Serializar los datos del equipo para que Vue los pueda usar
        equipment_data = model_to_dict(self.object)
        
        # Asegurarse de que el formato de fecha sea compatible con <input type="date">
        if equipment_data.get('date_purchase'):
            equipment_data['date_purchase'] = equipment_data['date_purchase'].strftime('%Y-%m-%d')
        else:
            equipment_data['date_purchase'] = ''

        context['equipment_data_json'] = json.dumps(equipment_data, cls=DjangoJSONEncoder)
        
        return context

    def get_success_url(self):
        url = reverse_lazy('resource_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url
        
    def post(self, request, *args, **kwargs):
        """Maneja solicitudes POST para actualizar recursos"""
        self.object = self.get_object()
        # Verificar si la solicitud es AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            # Si es AJAX, parsear los datos JSON
            if is_ajax:
                data = json.loads(request.body.decode('utf-8'))
                
                # Para todos los campos booleanos: si no están presentes, establecer como False
                # Primero obtenemos todos los campos booleanos del modelo
                boolean_fields = [field.name for field in ResourceItem._meta.fields 
                                if isinstance(field, models.BooleanField)]
                
                # Para cada campo booleano que no esté en data, establecerlo como False
                for field_name in boolean_fields:
                    if field_name not in data:
                        data[field_name] = False
                
                form = ResourceItemForm(data, instance=self.object)
            else:
                # Si es un POST normal, usar los datos del formulario
                form = ResourceItemForm(request.POST, instance=self.object)
            
            # Validar el formulario
            if form.is_valid():
                resource = form.save()
                
                # Si es AJAX, devolver respuesta JSON
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Recurso actualizado exitosamente',
                        'data': {
                            'id': resource.id,
                            'name': resource.name,
                            'code': resource.code,
                            'type': resource.type
                        },
                        'redirect': reverse_lazy('resource_detail', kwargs={'pk': resource.pk}) + '?action=updated'
                    })
                else:
                    # Si es un POST normal, redirigir a la vista de detalle
                    redirect_url = reverse_lazy('resource_detail', kwargs={'pk': resource.pk})
                    return HttpResponseRedirect(f'{redirect_url}?action=updated')
            else:
                # Si hay errores en el formulario
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': 'Error al validar los datos del recurso',
                        'errors': form.errors
                    }, status=400)
                else:
                    # Para POST normal, volver a renderizar el formulario con errores
                    context = self.get_context_data()
                    context['form'] = form
                    return render(request, self.template_name, context)
                    
        except json.JSONDecodeError:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Los datos enviados no son un JSON válido',
                }, status=400)
            return render(request, self.template_name, self.get_context_data())
        except Exception as e:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Error al actualizar el recurso: {str(e)}',
                }, status=500)
            context = self.get_context_data()
            context['error'] = f'Error al actualizar el recurso: {str(e)}'
            return render(request, self.template_name, context)
