from django.urls import path
from equipment.views import (
    VehicleCreateView,
    VehicleListView,
    VehicleUpdateView,
    VehicleDetailView,
    VehicleDeleteView,
    ResourceItemCreateUpdateView,
    ResourceItemDetailView,
    ResourceItemDeleteView,
    ResourceItemListView,
)

urlpatterns = [
    # Vehicle URLs
    path('vehiculos/', VehicleListView.as_view(), name='vehicle_list'),
    path('vehiculos/<int:pk>/', VehicleDetailView.as_view(), name='vehicle_detail'),
    path('vehiculos/crear/', VehicleCreateView.as_view(), name='vehicle_create'),
    path('vehiculos/editar/<int:pk>/', VehicleUpdateView.as_view(), name='vehicle_update'),
    path('vehiculos/eliminar/<int:pk>/', VehicleDeleteView.as_view(), name='vehicle_delete'),
    # ResourceItem URLs
    path('equipos/', ResourceItemListView.as_view(), name='resource_list'),
    path('equipos/<int:pk>/', ResourceItemDetailView.as_view(), name='resource_detail'),
    path('equipos/crear/', ResourceItemCreateUpdateView.as_view(), name='resource_create'),
    path('equipos/editar/<int:pk>/', ResourceItemCreateUpdateView.as_view(), name='resource_update'),
    path('equipos/eliminar/<int:pk>/', ResourceItemDeleteView.as_view(), name='resource_delete'),

]
