from django.urls import path
from api.vehicles import (
    CertVehicleCreateUpdateAPI,
    CertVehicleDeleteAPI,
    PassVehicleCreateUpdateAPI,
    PassVehicleDeleteAPI,
)

urlpatterns = [
    path('vehicles/cert_vehicle/', CertVehicleCreateUpdateAPI.as_view(), name='api_cert_vehicle_create_update'),
    path('vehicles/cert_vehicle/<int:pk>/', CertVehicleDeleteAPI.as_view(), name='api_cert_vehicle_delete'),
    path('vehicles/pass_vehicle/', PassVehicleCreateUpdateAPI.as_view(), name='api_pass_vehicle_create_update'),
    path('vehicles/pass_vehicle/<int:pk>/', PassVehicleDeleteAPI.as_view(), name='api_pass_vehicle_delete'),
]
