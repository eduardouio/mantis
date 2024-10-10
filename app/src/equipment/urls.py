from django.urls import path
from .views import ListEquipment

app_name = 'equipment'

urlpatterns = [
    path('equipos/', ListEquipment.as_view(), name='list'),
]
