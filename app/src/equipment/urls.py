from django.urls import path
from .views import ListEquipment, DetailEquipment, CreateEquipment

urlpatterns = [
    path('equipos/', ListEquipment.as_view(), name='equipment_list'),
    path('equipos/<int:pk>/', DetailEquipment.as_view(), name='equipment_detail'),
    path('equipos/crear/', CreateEquipment.as_view(), name='equipment_create'),
]
