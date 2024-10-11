from django.urls import path
from .views import (
    ListEquipment,
    DetailEquipment,
    CreateEquipment,
    UpdateEquipment,
    DeleteEquipment,
    ListVehicle,
    DetailVehicle,
    CreateVehicle,
    UpdateVehicle,
    DeleteVehicle
)

urlpatterns = [
    path('equipos/listar/', ListEquipment.as_view(), name='equipment_list'),
    path('equipos/<int:pk>/', DetailEquipment.as_view(), name='equipment_detail'),
    path('equipos/crear/', CreateEquipment.as_view(), name='equipment_create'),
    path('equipos/editar/<int:pk>/', UpdateEquipment.as_view(), name='equipment_update'),
    path('equipos/eliminar/<int:pk>/', DeleteEquipment.as_view(), name='equipment_delete'),
    
    path('vehiculos/listar/', ListVehicle.as_view(), name='vehicle_list'),
    path('vehiculos/<int:pk>/', DetailVehicle.as_view(), name='vehicle_detail'),
    path('vehiculos/crear/', CreateVehicle.as_view(), name='vehicle_create'),
    path('vehiculos/editar/<int:pk>/', UpdateVehicle.as_view(), name='vehicle_update'),
    path('vehiculos/eliminar/<int:pk>/', DeleteVehicle.as_view(), name='vehicle_delete'),
]
