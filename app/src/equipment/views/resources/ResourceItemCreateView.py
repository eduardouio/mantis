from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from equipment.models import ResourceItem
from equipment.forms.ResourceItemForm import ResourceItemForm


@method_decorator(csrf_exempt, name='dispatch')
class ResourceItemCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'forms/equipment_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nuevo Equipo'
        context['title_page'] = 'Registrar Nuevo Equipo'
        context['form'] = ResourceItemForm()  # Inicializar el formulario vacío
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """Maneja solicitudes POST para crear recursos"""
        # Verificar si la solicitud es AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            # Si es AJAX, parsear los datos JSON
            if is_ajax:
                data = json.loads(request.body.decode('utf-8'))
                form = ResourceItemForm(data)
            else:
                # Si es un POST normal, usar los datos del formulario
                form = ResourceItemForm(request.POST)
            
            # Validar el formulario
            if form.is_valid():
                resource = form.save()
                
                # Si es AJAX, devolver respuesta JSON
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Recurso guardado exitosamente',
                        'data': {
                            'id': resource.id,
                            'name': resource.name,
                            'code': resource.code,
                            'type': resource.type
                        },
                        'redirect': reverse_lazy('resource_detail', kwargs={'pk': resource.pk}) + '?action=created'
                    })
                else:
                    # Si es un POST normal, redirigir a la vista de detalle
                    redirect_url = reverse_lazy('resource_detail', kwargs={'pk': resource.pk})
                    return HttpResponseRedirect(f'{redirect_url}?action=created')
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
                    context = self.get_context_data(**kwargs)
                    context['form'] = form
                    return render(request, self.template_name, context)
                    
        except json.JSONDecodeError:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Los datos enviados no son un JSON válido',
                }, status=400)
            return render(request, self.template_name, self.get_context_data(**kwargs))
        except Exception as e:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Error al guardar el recurso: {str(e)}',
                }, status=500)
            context = self.get_context_data(**kwargs)
            context['error'] = f'Error al guardar el recurso: {str(e)}'
            return render(request, self.template_name, context)
