from django.urls import path
from api.vehicles import (
    CertVehicleCreateUpdateAPI,
    CertVehicleDeleteAPI,
    PassVehicleCreateUpdateAPI,
    PassVehicleDeleteAPI,
)

from api.technicals import (
    CreateUpdatePassTechnicalAPI,
    CreateUpdateVaccineAPI,
    DeletePassTechnicalAPI,
    DeleteVaccineAPI,
)

from api.resources import UpdateResourceAPI

from api.projects import (
    AddResourceProjectAPI,
    DeleteResourceProjectAPI,
    ResourcesAvailableAPI,
)

urlpatterns = [
    # vehicles
    path('vehicles/cert_vehicle/', CertVehicleCreateUpdateAPI.as_view(), name='api_cert_vehicle_create_update'),
    path('vehicles/cert_vehicle/<int:pk>/', CertVehicleDeleteAPI.as_view(), name='api_cert_vehicle_delete'),
    path('vehicles/pass_vehicle/', PassVehicleCreateUpdateAPI.as_view(), name='api_pass_vehicle_create_update'),
    path('vehicles/pass_vehicle/<int:pk>/', PassVehicleDeleteAPI.as_view(), name='api_pass_vehicle_delete'),
    # technicals
    path('technicals/create_update_pass_technical/', CreateUpdatePassTechnicalAPI.as_view(), name='api_create_update_pass_technical'),
    path('technicals/create_update_vaccine/', CreateUpdateVaccineAPI.as_view(), name='api_create_update_vaccine'),
    path('technicals/delete_pass_technical/', DeletePassTechnicalAPI.as_view(), name='api_delete_pass_technical'),
    path('technicals/delete_vaccine/', DeleteVaccineAPI.as_view(), name='api_delete_vaccine'),
    # resources
    path('resources/update/', UpdateResourceAPI.as_view(), name='api_update_resource'),
    # projects
    path('projects/resources/available', ResourcesAvailableAPI.as_view(), name='api_resources_available'),
    path('projects/resources/add', AddResourceProjectAPI.as_view(), name='api_add_resource_project'),
    path('projects/resources/delete', DeleteResourceProjectAPI.as_view(), name='api_delete_resource_project'),
]
