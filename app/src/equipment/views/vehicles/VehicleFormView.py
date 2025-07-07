from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
import json

from equipment.models import Vehicle, CertificationVehicle, PassVehicle
from equipment.forms import VehicleForm

class VehicleFormView(LoginRequiredMixin, CreateView):
    model = Vehicle
    template_name = 'forms/vehicle_form_vue.html'
    form_class = VehicleForm

    def get_success_url(self):
        return reverse_lazy('vehicle_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Nuevo Vehículo' if not self.object else 'Editar Vehículo'
        context['title_page'] = context['title_section']
        
        # Preparar datos iniciales para Vue
        if self.object:
            context['form_data'] = self.get_initial_data()
        
        return context
    
    def get_initial_data(self):
        """Obtener los datos iniciales del vehículo para Vue"""
        vehicle_data = model_to_dict(self.object)
        
        # Obtener certificaciones
        certifications = list(self.object.certifications.values(
            'id', 'name', 'date_start', 'date_end', 'description', 'is_active'
        ))
        
        # Obtener pases
        passes = list(self.object.passes.values('id', 'bloque', 'fecha_caducidad'))
        
        # Formatear fechas
        for cert in certifications:
            cert['date_start'] = cert['date_start'].isoformat() if cert['date_start'] else None
            cert['date_end'] = cert['date_end'].isoformat() if cert['date_end'] else None
        
        for p in passes:
            p['fecha_caducidad'] = p['fecha_caducidad'].isoformat() if p['fecha_caducidad'] else None
        
        return json.dumps({
            'vehicle': vehicle_data,
            'certifications': certifications,
            'passes': passes
        })

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Manejar peticiones AJAX"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_ajax(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
    
    def handle_ajax(self, request, *args, **kwargs):
        """Manejar diferentes acciones AJAX"""
        if request.method == 'POST':
            return self.handle_post(request)
        elif request.method == 'PUT':
            return self.handle_put(request)
        else:
            return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    def handle_post(self, request):
        """Manejar creación de vehículos vía AJAX"""
        try:
            data = json.loads(request.body)
            form = self.get_form()
            
            # Crear instancia del formulario con los datos
            form = self.form_class(data)
            
            if form.is_valid():
                with transaction.atomic():
                    self.object = form.save(commit=False)
                    self.object.created_by = request.user
                    self.object.save()
                    
                    # Procesar certificaciones
                    certifications = json.loads(data.get('certifications_data', '[]'))
                    self.create_certifications(certifications)
                    
                    # Procesar pases
                    passes = json.loads(data.get('passes_data', '[]'))
                    self.create_passes(passes)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Vehículo creado correctamente',
                    'id': self.object.id,
                    'redirect_url': self.get_success_url()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario',
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    def handle_put(self, request):
        """Manejar actualización de vehículos vía AJAX"""
        try:
            data = json.loads(request.body)
            self.object = self.get_object()
            
            # Actualizar el vehículo
            form = self.form_class(data, instance=self.object)
            
            if form.is_valid():
                with transaction.atomic():
                    self.object = form.save(commit=False)
                    self.object.updated_by = request.user
                    self.object.save()
                    
                    # Eliminar certificaciones existentes
                    self.object.certifications.all().delete()
                    
                    # Procesar nuevas certificaciones
                    certifications = json.loads(data.get('certifications_data', '[]'))
                    self.create_certifications(certifications)
                    
                    # Eliminar pases existentes
                    self.object.passes.all().delete()
                    
                    # Procesar nuevos pases
                    passes = json.loads(data.get('passes_data', '[]'))
                    self.create_passes(passes)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Vehículo actualizado correctamente',
                    'id': self.object.id,
                    'redirect_url': self.get_success_url()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario',
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    def create_certifications(self, certifications_data):
        """Crear certificaciones para el vehículo"""
        for cert_data in certifications_data:
            # Eliminar el ID temporal si existe
            cert_data.pop('id', None)
            
            # Crear la certificación
            CertificationVehicle.objects.create(
                vehicle=self.object,
                created_by=self.request.user,
                **cert_data
            )
    
    def create_passes(self, passes_data):
        """Crear pases para el vehículo"""
        for pass_data in passes_data:
            # Eliminar el ID temporal si existe
            pass_data.pop('id', None)
            
            # Crear el pase
            PassVehicle.objects.create(
                vehicle=self.object,
                created_by=self.request.user,
                **pass_data
            )

class VehicleCreateView(VehicleFormView):
    """Vista para crear vehículos"""
    pass

class VehicleUpdateView(VehicleFormView, UpdateView):
    """Vista para actualizar vehículos"""
    def get_queryset(self):
        return Vehicle.objects.filter(pk=self.kwargs['pk'])
