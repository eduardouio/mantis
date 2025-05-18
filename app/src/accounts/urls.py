from django.urls import path
from .views import (
    HomeTV,
    LoginTV,
    LogoutRV,
    ListTechnical,
    TechnicalDetail,
    DetailLicense,
    CreateTechnical,
    UpdateTechnical,
    DeleteTechnical,
    ListLicense,
    CreateLicense,
    UpdateLicense,
    DeleteLicense
)


urlpatterns = [
    # cuentas
    path('', HomeTV.as_view(), name='home'),
    path('accounts/login/', LoginTV.as_view(), name='login'),
    path('accounts/logout/', LogoutRV.as_view(), name='logout'),
    # Tecnicos
    path('tecnicos/', ListTechnical.as_view(), name='technical_list'),
    path('tecnicos/<int:pk>/', TechnicalDetail.as_view(), name='technical_detail'),
    path('tecnicos/create/', CreateTechnical.as_view(), name='technical_create'),
    path('tecnicos/update/<int:pk>/', UpdateTechnical.as_view(), name='technical_update'),
    path('tecnicos/delete/<int:pk>/', DeleteTechnical.as_view(), name='technical_delete'),
    # Licencias
    path('licencias/', ListLicense.as_view(), name='license_list'),
    path('licencias/<int:pk>/', DetailLicense.as_view(), name='license_detail'),
    path('licencias/create/', CreateLicense.as_view(), name='license_create'),
    path('licencias/update/<int:pk>/', UpdateLicense.as_view(), name='license_update'),
    path('licencias/delete/<int:pk>/', DeleteLicense.as_view(), name='license_delete'),
]
