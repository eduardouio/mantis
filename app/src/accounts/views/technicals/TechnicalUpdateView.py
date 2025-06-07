from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.models import Technical
from accounts.forms.TechnicalForm import TechnicalForm


class TechnicalUpdateView(LoginRequiredMixin, UpdateView):
    model = Technical
    template_name = 'forms/technical_form.html'
    form_class = TechnicalForm
    # success_url = '/tecnicos/' # Se reemplaza por get_success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Técnico {}'.format(
            self.object.first_name)
        context['title_page'] = 'Actualizar Técnico {}'.format(
            self.object.first_name)
        return context

    def get_success_url(self):
        messages.success(self.request, f'Técnico {self.object.first_name} {self.object.last_name} actualizado exitosamente.')
        url = reverse_lazy('technical_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url

    def form_valid(self, form):
        messages.success(self.request, 'Los datos del técnico han sido actualizados correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar los datos. Por favor, revise los campos.')
        return super().form_invalid(form)


class TechnicalCreateView(LoginRequiredMixin, CreateView):
    model = Technical
    template_name = 'forms/technical_form.html'
    form_class = TechnicalForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = 'Nuevo Técnico'
        context['title_section'] = 'Formulario de Técnico'
        return context

    def get_success_url(self):
        messages.success(self.request, f'Técnico {self.object.first_name} {self.object.last_name} creado exitosamente.')
        return reverse_lazy('technical_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Establecer valores por defecto si es necesario
        if not form.cleaned_data.get('is_active'):
            form.instance.is_active = True
        
        messages.success(self.request, 'El técnico ha sido creado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al crear el técnico. Por favor, revise los campos.')
        return super().form_invalid(form)
