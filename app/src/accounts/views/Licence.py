from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    RedirectView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import License
from django import forms

class LicenseForm(forms.ModelForm):
    class Meta:
        model = License
        fields = [
            'license_key', 'activated_on', 'expires_on', 'licence_file',
            'role', 'enterprise', 'is_active', 'url_server', 'user'
        ]
        widgets = {
            'license_key': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'activated_on': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'expires_on': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'licence_file': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'role': forms.Select(attrs={'class': 'form-select form-control-sm'}),
            'enterprise': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'url_server': forms.URLInput(attrs={'class': 'form-control form-control-sm'}),
            'user': forms.Select(attrs={'class': 'form-select form-control-sm'}),
        }


class ListLicense(LoginRequiredMixin, ListView):
    model = License
    template_name = 'lists/license_list.html'
    context_object_name = 'licenses'
    ordering = ['license_key']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado De Licencias Registradas'
        context['title_page'] = 'Listado De Licencias'

        if 'action' not in self.request.GET:
            return context
        message = ''
        if self.request.GET.get('action') == 'deleted':
            message = 'La licencia ha sido eliminada con éxito.'

        context['action'] = self.request.GET.get('action')
        context['message'] = message
        return context


class DetailLicense(LoginRequiredMixin, DetailView):
    model = License
    template_name = 'presentations/license_presentation.html'
    context_object_name = 'license'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle de la Licencia {}'.format(
            self.object.license_key
        )
        context['title_page'] = 'Detalle de la Licencia {}'.format(
            self.object.license_key
        )

        if 'action' not in self.request.GET:
            return context

        context['action'] = self.request.GET.get('action')
        context['license'] = self.object
        message = ''
        if context['action'] == 'created':
            message = 'La licencia ha sido creada con éxito.'
        elif context['action'] == 'updated':
            message = 'La licencia ha sido actualizada con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No es posible eliminar la licencia. Existen dependencias.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'

        context['message'] = message
        return context


class CreateLicense(LoginRequiredMixin, CreateView):
    model = License
    template_name = 'forms/license_form.html'
    form_class = LicenseForm
    success_url = '/licencias/'

    def get_success_url(self):
        url = reverse_lazy('license_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=created'
        return url


class UpdateLicense(LoginRequiredMixin, UpdateView):
    model = License
    template_name = 'forms/license_form.html'
    form_class = LicenseForm
    success_url = '/licencias/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Licencia {}'.format(
            self.object.license_key
        )
        context['title_page'] = 'Actualizar Licencia {}'.format(
            self.object.license_key
        )
        return context

    def get_success_url(self):
        url = reverse_lazy('license_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url


class DeleteLicense(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        license = License.objects.get(pk=kwargs['pk'])
        try:
            license.delete()
            url = reverse_lazy('license_list')
            return f'{url}?action=deleted'
        except Exception as e:
            return f'{reverse_lazy("license_detail", 
                                    kwargs={"pk": kwargs["pk"]}
                )}?action=no_delete'
