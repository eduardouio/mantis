from django.urls import path
from filemanager.views import FileManagerView, ProjectDocumentsView

urlpatterns = [
    path('documentos/', FileManagerView.as_view(), name='file_manager'),
    path('documentos/proyecto/<int:pk>/', ProjectDocumentsView.as_view(), name='project_documents'),
]
