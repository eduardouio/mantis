from django.urls import path
from projects.views import (
    PartnerListView,
    PartnerDetailView,
    PartnerCreateView,
    PartnerUpdateView,
    PartnerDeleteView,
    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
)

urlpatterns = [
    path('socios/', PartnerListView.as_view(), name='partner_list'),
    path('socios/<int:pk>/', PartnerDetailView.as_view(), name='partner_detail'),
    path('socios/create/', PartnerCreateView.as_view(), name='partner_create'),
    path('socios/update/<int:pk>/', PartnerUpdateView.as_view(), name='partner_update'),
    path('socios/delete/<int:pk>/', PartnerDeleteView.as_view(), name='partner_delete'),
    # projects
    path('proyectos/', ProjectListView.as_view(), name='project_list'),
    path('proyectos/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('proyectos/create/', ProjectCreateView.as_view(), name='project_create'),
    path('proyectos/update/<int:pk>/', ProjectUpdateView.as_view(), name='project_update'),
    path('proyectos/delete/<int:pk>/', ProjectDeleteView.as_view(), name='project_delete'),
    
]