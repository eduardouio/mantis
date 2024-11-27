from django.urls import path
from .views import (
    ListPartner,
    DetailPartner,
    CreatePartner,
    UpdatePartner,
    DeletePartner,
    ListProject,
    DetailProject,
    CreateProject,
    UpdateProject,
    DeleteProject,
    APIAddManyToMany,
    AddEquipmentProject,
    RemoveEquipmentProject,
    UpdateEquipmentProject,
    CreateProjectResource,
    UpdateProjectResource,
    DeleteProjectResource,
)

urlpatterns = [
    path('socios/', ListPartner.as_view(), name='partner_list'),
    path('socios/<int:pk>/', DetailPartner.as_view(), name='partner_detail'),
    path('socios/create/', CreatePartner.as_view(), name='partner_create'),
    path('socios/update/<int:pk>/', UpdatePartner.as_view(), name='partner_update'),
    path('socios/delete/<int:pk>/', DeletePartner.as_view(), name='partner_delete'),
    path('socios/add/many-deps/', APIAddManyToMany.as_view(), name='partner_add_many_to_many'),
    # projects
    path('proyectos/', ListProject.as_view(), name='project_list'),
    path('proyectos/<int:pk>/', DetailProject.as_view(), name='project_detail'),
    path('proyectos/create/', CreateProject.as_view(), name='project_create'),
    path('proyectos/update/<int:pk>/', UpdateProject.as_view(), name='project_update'),
    path('proyectos/delete/<int:pk>/', DeleteProject.as_view(), name='project_delete'),
    path('proyectos/add/equipment/', AddEquipmentProject.as_view(), name='project_add_equipment'),
    path('proyectos/remove/equipment/', RemoveEquipmentProject.as_view(), name='project_delete_equipment'),
    path('proyectos/update/equipment/', UpdateEquipmentProject.as_view(), name='project_update_equipment'),
    # project resources
    path('proyectos/add/resource/', CreateProjectResource.as_view(), name='project_add_resource'),
    path('proyectos/update/resource/', UpdateProjectResource.as_view(), name='project_update_resource'),\
    path('proyectos/delete/resource/', DeleteProjectResource.as_view(), name='project_delete_resource'),
    
]