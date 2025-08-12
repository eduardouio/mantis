from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.models import Technical
from accounts.forms.TechnicalForm import TechnicalForm


class TechnicalUpdateView(LoginRequiredMixin, UpdateView):
    model = Technical
    template_name = 'forms/technical_form.html'
    form_class = TechnicalForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Técnico {}'.format(
            self.object.first_name)
        context['title_page'] = 'Actualizar Técnico {}'.format(
            self.object.first_name)
        return context

    def get_success_url(self):
        messages.success(
            self.request,
            f'Técnico {self.object.first_name} {self.object.last_name} '
            f'actualizado exitosamente.'
        )
        url = reverse_lazy('technical_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url

    def form_valid(self, form):
        """Guardar el técnico"""
        messages.success(
            self.request,
            'Los datos del técnico han sido actualizados correctamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Ha ocurrido un error al actualizar los datos. '
            'Por favor, revise los campos.'
        )
        return super().form_invalid(form)
