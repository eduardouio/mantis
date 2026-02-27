from django.urls import path
from filemanager.views import FileManagerView

urlpatterns = [
    path('documentos/', FileManagerView.as_view(), name='file_manager'),
]
