from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
)
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from datetime import date # Asegúrate de importar date

from accounts.models import Technical
from accounts.forms import TechnicalForm


# Función auxiliar para calcular detalles de caducidad
def get_expiry_details(expiry_date):
    if not expiry_date:
        return {"text": "N/A", "class": "text-gray-500"}

    today = date.today()
    delta = expiry_date - today
    days_remaining = delta.days

    if days_remaining < 0:
        return {"text": "Vencido", "class": "text-error font-bold"}
    elif days_remaining == 0:
        return {"text": "Vence Hoy", "class": "text-error font-bold"}
    elif days_remaining <= 30:
        days_str = f"{days_remaining} día{'s' if days_remaining != 1 else ''}"
        return {"text": days_str, "class": "text-error font-semibold"}
    else:
        days_str = f"{days_remaining} día{'s' if days_remaining != 1 else ''}"
        return {"text": days_str, "class": "text-success font-semibold"}


class HomeTV(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


class ListTechnical(LoginRequiredMixin, ListView):
    model = Technical
    template_name = 'lists/technical_list.html'
    context_object_name = 'technicals'
    ordering = ['first_name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Técnicos'
        context['title_page'] = 'Listado de Técnicos'

        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'El técnico ha sido eliminado con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context


class DetailTechnical(LoginRequiredMixin, DetailView):
    model = Technical
    template_name = 'presentations/technical_presentation.html'
    context_object_name = 'technical'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = 'Ficha de Técnico'
        context['title_section'] = 'Ficha de Técnico'
        context['action'] = self.request.GET.get('action', None)
        
        technical = self.object

        # Calcular detalles de caducidad para cada fecha relevante
        context['license_expiry_details'] = get_expiry_details(technical.license_expiry_date)
        context['defensive_driving_expiry_details'] = get_expiry_details(technical.defensive_driving_certificate_expiry_date)
        context['mae_expiry_details'] = get_expiry_details(technical.mae_certificate_expiry_date)
        context['medical_expiry_details'] = get_expiry_details(technical.medical_certificate_expiry_date)
        context['quest_end_details'] = get_expiry_details(technical.quest_end_date)
        
        return context

class CreateTechnical(LoginRequiredMixin, CreateView):
    model = Technical
    template_name = 'forms/technical_form.html'
    form_class = TechnicalForm
    success_url = '/tecnicos/'

    def get_success_url(self):
        url = reverse_lazy('technical_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nuevo Técnico'
        context['title_page'] = 'Registrar Nuevo Técnico'
        return context


class UpdateTechnical(LoginRequiredMixin, UpdateView):
    model = Technical
    template_name = 'forms/technical_form.html'
    form_class = TechnicalForm
    success_url = '/tecnicos/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Técnico {}'.format(
            self.object.first_name)
        context['title_page'] = 'Actualizar Técnico {}'.format(
            self.object.first_name)
        return context

    def get_success_url(self):
        url = reverse_lazy('technical_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url


class DeleteTechnical(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        technical = Technical.objects.get(pk=kwargs['pk'])
        try:
            technical.delete()
            url = reverse_lazy('technical_list')
            return f'{url}?action=deleted'
        except Exception as e:
            url = reverse_lazy('technical_detail', kwargs={'pk': technical.pk})
            return f'{url}?action=no_delete'
