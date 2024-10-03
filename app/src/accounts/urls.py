from django.urls import path
from .views import HomeTV

app_name = 'accounts'

urlpatterns = [
    path('', HomeTV.as_view(), name='home'),
]
