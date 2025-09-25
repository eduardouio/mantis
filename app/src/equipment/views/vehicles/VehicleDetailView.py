from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from equipment.models import Vehicle
from equipment.models.CertificationVehicle import CertificationVehicle
from equipment.models.PassVehicle import PassVehicle


class VehicleDetailView(DetailView):
    model = Vehicle
    template_name = 'presentations/vehicle_presentation.html'
    context_object_name = 'vehicle'

    def get_object(self, queryset=None):
        return get_object_or_404(Vehicle, pk=self.kwargs['pk'], is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.get_object()

        # Obtener certificaciones del vehículo
        context['certifications'] = CertificationVehicle.objects.filter(
            vehicle=vehicle, is_active=True
        ).order_by('-date_start')

        # Obtener pases del vehículo
        context['passes'] = PassVehicle.get_by_vehicle(vehicle.id)

        # Opciones para formularios
        context['certification_choices'] = (
            CertificationVehicle.CERTIFICATION_NAME_CHOICES
        )
        context['pass_bloque_choices'] = PassVehicle.BLOQUE_CHOICES

        # Información de auditoría
        context['created_user'] = vehicle.get_create_user()
        context['updated_user'] = vehicle.get_update_user()

        return context
