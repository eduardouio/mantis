from django.urls import path
from .views import (
    HomeTV,
    LoginTV,
    LogoutRV,
    TechnicalCreateView,
    TechnicalDeleteView,
    TechnicalDetailView,
    TechnicalListView,
    TechnicalUpdateView,
    LicenseCreateView,
    LicenseDetailView,
    LicenseUpdateView,
    LicenseDeleteView,
    LicenseListView,
)

from accounts.views.technicals.TechnicalDeactivateView import TechnicalDeactivateView


urlpatterns = [
    # cuentas
    path('', HomeTV.as_view(), name='home'),
    path('accounts/login/', LoginTV.as_view(), name='login'),
    path('accounts/logout/', LogoutRV.as_view(), name='logout'),
    # Tecnicos
    path('tecnicos/', TechnicalListView.as_view(), name='technical_list'),
    path('tecnicos/<int:pk>/', TechnicalDetailView.as_view(), name='technical_detail'),
    path('tecnicos/nuevo/', TechnicalCreateView.as_view(), name='technical_create'),
    path('tecnicos/actualizar/<int:pk>/', TechnicalUpdateView.as_view(), name='technical_update'),
    path('tecnicos/eliminar/<int:pk>/', TechnicalDeleteView.as_view(), name='technical_delete'),
    path('tecnicos/desactivar/<int:pk>/', TechnicalDeactivateView.as_view(), name='technical_deactivate'),
    # Licencias
    path('licencias/', LicenseListView.as_view(), name='license_list'),
    path('licencias/<int:pk>/', LicenseDetailView.as_view(), name='license_detail'),
    path('licencias/nuevo/', LicenseCreateView.as_view(), name='license_create'),
    path('licencias/actualizar/<int:pk>/', LicenseUpdateView.as_view(), name='license_update'),
    path('licencias/eliminar/<int:pk>/', LicenseDeleteView.as_view(), name='license_delete'),
]
