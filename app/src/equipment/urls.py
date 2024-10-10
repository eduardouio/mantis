from django.urls import path
from .views import ListEquipment, DetailEquipment

urlpatterns = [
    path('equipos/', ListEquipment.as_view(), name='equipment_list'),
    path('equipos/<int:pk>/', DetailEquipment.as_view(), name='equipment_detail'),
]
