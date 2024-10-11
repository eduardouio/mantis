from django.urls import path
from .views import (
    ListPartner,
    DetailPartner,
    CreatePartner,
    UpdatePartner,
    DeletePartner
)

urlpatterns = [
    path('socios/', ListPartner.as_view(), name='partner_list'),
    path('socios/<int:pk>/', DetailPartner.as_view(), name='partner_detail'),
    path('socios/create/', CreatePartner.as_view(), name='partner_create'),
    path('socios/update/<int:pk>/', UpdatePartner.as_view(), name='partner_update'),
    path('socios/delete/<int:pk>/', DeletePartner.as_view(), name='partner_delete'),
]