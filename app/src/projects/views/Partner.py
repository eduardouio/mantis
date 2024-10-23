import json
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    RedirectView
)
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from projects.models import Partner
from equipment.models import Vehicle
from accounts.models import Technical


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = [
            'business_tax_id', 'name', 'email', 'phone', 'address',
            'name_contact'
        ]
        widgets = {
            'business_tax_id': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'address': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'name_contact': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }


class ListPartner(LoginRequiredMixin, ListView):
    model = Partner
    template_name = 'lists/partner_list.html'
    context_object_name = 'partners'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Socios de Negocio Registrados'
        context['title_page'] = 'Listado de Socios de Negocio'

        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'El socio de negocio ha sido eliminado con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context


class DetailPartner(LoginRequiredMixin, DetailView):
    model = Partner
    template_name = 'presentations/partner_presentation.html'
    context_object_name = 'partner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle del Socio de Negocio {}'.format(
            self.object.business_tax_id
        )
        context['title_page'] = 'Detalle del Socio de Negocio {}'.format(
            self.object.business_tax_id
        )

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        context['partner'] = self.object
        message = ''
        if context['action'] == 'created':
            message = 'El socio de negocio ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El socio de negocio ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No es posible eliminar el socio de negocio. Existen dependencias.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'

        context['message'] = message
        return context


class CreatePartner(LoginRequiredMixin, CreateView):
    model = Partner
    template_name = 'forms/partner_form.html'
    form_class = PartnerForm
    success_url = '/socios/'

    def get_success_url(self):
        url = reverse_lazy('partner_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Registrar Nuevo Socio de Negocio'
        context['title_page'] = 'Registrar Nuevo Socio de Negocio'
        return context


class UpdatePartner(LoginRequiredMixin, UpdateView):
    model = Partner
    template_name = 'forms/partner_form.html'
    form_class = PartnerForm
    success_url = '/socios/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Socio de Negocio {}'.format(
            self.object.business_tax_id
        )
        context['title_page'] = 'Actualizar Socio de Negocio {}'.format(
            self.object.business_tax_id
        )
        vehicles = Vehicle.get_true_false_list(self.object)
        technicals = Technical.get_true_false_list(self.object)

        context['vehicles'] = json.dumps(vehicles)
        context['technicals'] = json.dumps(technicals)
        return context

    def get_success_url(self):
        url = reverse_lazy('partner_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url


class DeletePartner(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        partner = Partner.objects.get(pk=kwargs['pk'])
        try:
            partner.delete()
            url = reverse_lazy('partner_list')
            return f'{url}?action=deleted'
        except Exception as e:
            url = reverse_lazy('partner_detail', kwargs={'pk': partner.pk})
            return f'{url}?action=no_delete'


class APIAddManyToMany(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        partner = Partner.objects.get(pk=data['partner_id'])
        if data['type'] == 'vehicle':
            vehicle = Vehicle.objects.get(pk=data['id'])
            if data['action'] == 'add':
                partner.authorized_vehicle.add(vehicle)
                partner.save()
            else:
                partner.authorized_vehicle.remove(vehicle)
                partner.save()

        if data['type'] == 'technical':
            technical = Technical.objects.get(pk=data['id'])
            if data['action'] == 'add':
                partner.authorized_tehcnicals.add(technical)
                partner.save()
            else:
                partner.authorized_tehcnicals.remove(technical)
                partner.save()

        return JsonResponse({'status': 'ok'}, status=200)
