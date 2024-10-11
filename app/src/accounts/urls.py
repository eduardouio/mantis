from django.urls import path
from .views import (
    HomeTV,
    LoginTV,
    LogoutRV,
    ListTechnical,
    DetailTechnical,
    CreateTechnical,
    UpdateTechnical,
    DeleteTechnical
)


urlpatterns = [
    # cuentas
    path('', HomeTV.as_view(), name='home'),
    path('accounts/login/', LoginTV.as_view(), name='login'),
    path('accounts/logout/', LogoutRV.as_view(), name='logout'),
    # Tecnicos
    path('tecnicos/', ListTechnical.as_view(), name='technical_list'),
    path('tecnicos/<int:pk>/', DetailTechnical.as_view(), name='technical_detail'),
    path('tecnicos/create/', CreateTechnical.as_view(), name='technical_create'),
    path('tecnicos/update/<int:pk>/', UpdateTechnical.as_view(), name='technical_update'),
    path('tecnicos/delete/<int:pk>/', DeleteTechnical.as_view(), name='technical_delete'),

]
