from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from equipment.models import ResourceItem


class ResourceItemDeleteView(LoginRequiredMixin, RedirectView):
    """
    Vista para eliminar un recurso (soft delete).
    Actualiza el campo is_active a False en lugar de eliminar el registro.
    """

    def get_redirect_url(self, *args, **kwargs):
        try:
            # Obtener el equipo y marcar como inactivo en lugar de eliminarlo
            equipment = ResourceItem.objects.get(pk=kwargs['pk'])

            # Verificar si el equipo ya está inactivo
            if not equipment.is_active:
                messages.warning(
                    self.request,
                    _('El recurso ya ha sido eliminado anteriormente.')
                )
                return reverse_lazy('resource_list')

            # Realizar soft delete
            equipment.is_active = False
            equipment.save(update_fields=['is_active', 'updated_at'])

            # Mensaje de éxito
            messages.success(
                self.request,
                _('Recurso eliminado exitosamente.')
            )

            # Redirigir a la lista de recursos con parámetro de éxito
            url = reverse_lazy('resource_list')
            return f'{url}?action=deleted&resource_id={equipment.id}'

        except ResourceItem.DoesNotExist:
            # Si el recurso no existe, redirigir con mensaje de error
            messages.error(
                self.request,
                _('El recurso que intenta eliminar no existe.')
            )
            return reverse_lazy('resource_list')

        except Exception as e:
            # Manejar cualquier otro error inesperado
            messages.error(
                self.request,
                _('Ocurrió un error al intentar eliminar el recurso: {}').format(str(e))
            )
            if 'equipment' in locals():
                return reverse_lazy('resource_detail', kwargs={'pk': equipment.pk})
            return reverse_lazy('resource_list')
