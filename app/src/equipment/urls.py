from django.urls import path
from .views import (
    ListEquipment,
    DetailEquipment,
    CreateEquipment,
    UpdateEquipment,
    DeleteEquipment
)

urlpatterns = [
    path('equipos/listar/', ListEquipment.as_view(), name='equipment_list'),
    path('equipos/<int:pk>/', DetailEquipment.as_view(), name='equipment_detail'),
    path('equipos/crear/', CreateEquipment.as_view(), name='equipment_create'),
    path('equipos/editar/<int:pk>/', UpdateEquipment.as_view(), name='equipment_update'),
    path('equipos/eliminar/<int:pk>/', DeleteEquipment.as_view(), name='equipment_delete'),
]
