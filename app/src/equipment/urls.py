from django.urls import path
from equipment.views import (
    VehicleCreateView,
    VehicleListView,
    VehicleUpdateView,
    VehicleDetailView,
    VehicleDeleteView
)

urlpatterns = [
    path('vehiculos/listar/', VehicleListView.as_view(), name='vehicle_list'),
    path('vehiculos/<int:pk>/', VehicleDetailView.as_view(), name='vehicle_detail'),
    path('vehiculos/crear/', VehicleCreateView.as_view(), name='vehicle_create'),
    path('vehiculos/editar/<int:pk>/', VehicleUpdateView.as_view(), name='vehicle_update'),
    path('vehiculos/eliminar/<int:pk>/', VehicleDeleteView.as_view(), name='vehicle_delete'),
]
