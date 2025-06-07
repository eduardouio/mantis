from .HomeTV import HomeTV
from .LoginTV import LoginTV
from .LogoutRV import LogoutRV

from accounts.views.licenses import (
    LicenseCreateView,
    LicenseDeleteView,
    LicenseDetailView,
    LicenseListView,
    LicenseUpdateView,

)

from accounts.views.technicals import (
    TechnicalCreateView,
    TechnicalDeleteView,
    TechnicalDetailView,
    TechnicalListView,
    TechnicalUpdateView
)


__all__ = [
    'HomeTV',
    'LoginTV',
    'LogoutRV',
    'TechnicalListView',
    'TechnicalDetailView',
    'TechnicalCreateView',
    'TechnicalUpdateView',
    'TechnicalDeleteView',
    'LicenseDetailView',
    'LicenseCreateView',
    'LicenseUpdateView',
    'LicenseDeleteView',
    'LicenseListView'
]
