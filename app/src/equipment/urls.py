from django.urls import path
from .views import (
    ResourceItemList,
    ResourceItemDetail,
    CreateResourceItem,
    UpdateResourceItem,
    RemoveResourceItem,
    ListVehicle,
    DetailVehicle,
    CreateVehicle,
    UpdateVehicle,
    DeleteVehicle
)

urlpatterns = [
    path('recursos/listar/', ResourceItemList.as_view(), name='resource_list'),
    path('recursos/<int:pk>/', ResourceItemDetail.as_view(), name='resource_detail'),
    path('recursos/crear/', CreateResourceItem.as_view(), name='resource_create'),
    path('recursos/editar/<int:pk>/', UpdateResourceItem.as_view(), name='resource_update'),
    path('recursos/eliminar/<int:pk>/', RemoveResourceItem.as_view(), name='resource_delete'),

    path('vehiculos/listar/', ListVehicle.as_view(), name='vehicle_list'),
    path('vehiculos/<int:pk>/', DetailVehicle.as_view(), name='vehicle_detail'),
    path('vehiculos/crear/', CreateVehicle.as_view(), name='vehicle_create'),
    path('vehiculos/editar/<int:pk>/', UpdateVehicle.as_view(), name='vehicle_update'),
    path('vehiculos/eliminar/<int:pk>/', DeleteVehicle.as_view(), name='vehicle_delete'),
]
