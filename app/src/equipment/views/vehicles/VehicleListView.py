from django.views.generic import ListView
from django.db.models import Q, Prefetch
from equipment.models import Vehicle
from equipment.models.CertificationVehicle import CertificationVehicle
from django.contrib.auth.mixins import LoginRequiredMixin
from equipment.models.PassVehicle import PassVehicle


class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'lists/vehicle_list.html'
    context_object_name = 'vehicles'

    def get_queryset(self):
        queryset = Vehicle.get_all().select_related().prefetch_related(
            Prefetch(
                'certificationvehicle_set',
                queryset=CertificationVehicle.objects.filter(is_active=True),
                to_attr='certifications'
            ),
            Prefetch(
                'passvehicle_set',
                queryset=PassVehicle.objects.filter(is_active=True),
                to_attr='passes'
            )
        )

        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(no_plate__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search) |
                Q(serial_number__icontains=search) |
                Q(engine_number__icontains=search) |
                Q(chassis_number__icontains=search)
            )

        # Filtros específicos
        type_vehicle = self.request.GET.get('type_vehicle')
        if type_vehicle:
            queryset = queryset.filter(type_vehicle=type_vehicle)

        status_vehicle = self.request.GET.get('status_vehicle')
        if status_vehicle:
            queryset = queryset.filter(status_vehicle=status_vehicle)

        owner_transport = self.request.GET.get('owner_transport')
        if owner_transport:
            queryset = queryset.filter(owner_transport=owner_transport)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['type_vehicle'] = self.request.GET.get('type_vehicle', '')
        context['status_vehicle'] = self.request.GET.get('status_vehicle', '')
        context['owner_transport'] = self.request.GET.get(
            'owner_transport', '')
        context['vehicle_types'] = Vehicle._meta.get_field(
            'type_vehicle').choices
        context['vehicle_statuses'] = Vehicle._meta.get_field(
            'status_vehicle').choices
        context['owner_choices'] = Vehicle._meta.get_field(
            'owner_transport').choices

        return context
