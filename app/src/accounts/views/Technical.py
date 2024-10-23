from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, RedirectView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Technical
from django import forms


class TechnicalForm(forms.ModelForm):
    class Meta:
        model = Technical
        fields = [
            'date_joined', 'first_name', 'last_name', 'email', 'location', 'dni',
            'user', 'nro_phone', 'role', 'days_to_work', 'days_free', 'is_active'
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
            'location': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'dni': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'user': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'nro_phone': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'role': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'days_to_work': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'days_free': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


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
        context['title_section'] = 'Detalle del Técnico {}'.format(
            self.object.first_name)
        context['title_page'] = 'Detalle del Técnico {}'.format(
            self.object.first_name)

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        context['technical'] = self.object
        message = ''
        if context['action'] == 'created':
            message = 'El técnico ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El técnico ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No es posible eliminar el técnico. Existen dependencias.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'
        elif context['action'] == 'popup_window':
            context['popup_window'] = True

        context['message'] = message
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
