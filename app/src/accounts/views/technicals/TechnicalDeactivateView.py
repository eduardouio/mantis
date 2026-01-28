from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from accounts.models import Technical


class TechnicalDeactivateView(LoginRequiredMixin, View):
    """
    Vista para desactivar un técnico (eliminación lógica)
    Cambia el estado de is_active a False
    """
    
    def post(self, request, *args, **kwargs):
        technical = get_object_or_404(Technical, pk=kwargs['pk'])
        
        # Cambiar el estado a inactivo
        technical.is_active = False
        technical.save()
        
        messages.success(
            request,
            f'El técnico {technical.first_name} {technical.last_name} '
            f'ha sido desactivado exitosamente.'
        )
        
        # Redirigir a la lista de técnicos
        return redirect(reverse_lazy('technical_list'))
