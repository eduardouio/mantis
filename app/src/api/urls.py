from django.urls import path
from api.vehicles import (
    CertVehicleCreateUpdateAPI,
    CertVehicleDeleteAPI,
    PassVehicleCreateUpdateAPI,
    PassVehicleDeleteAPI,
)

from api.technicals import (
    CreateUpdatePassTechnicalAPI,
    CreateUpdateVaccineAPI,
    DeletePassTechnicalAPI,
    DeleteVaccineAPI,
)

from api.resources import UpdateResourceAPI

from api.projects import (
    AddResourceProjectAPI,
    DeleteResourceProjectAPI,
    ResourcesAvailableAPI,
)

from api.workorders import (
    AddUpdateSheetProjectAPI,
    GetAllSheetProjectAPI,
    DeleteSheetOrderAPI,
)

from api.projects.ProjectResources import ProjectResources
from api.projects.ProjectData import ProjectData
from api.workorders.GetAllSheerProjectItems import GetAllSheerProjectItemsAPI
from api.workorders.CreateCustodyChain import CreateCustodyChainAPI
from api.projects.UpdateResourceItem import UpdateResourceItemAPI
from api.vehicles.GetVehiclesAvaliablesAPI import GetVehiclesAvaliablesAPI
from api.technicals.GetTechnicalsAvaliablesAPI import GetTechnicalsAvaliablesAPI

urlpatterns = [
    # vehicles
    path('vehicles/cert_vehicle/', CertVehicleCreateUpdateAPI.as_view(), name='api_cert_vehicle_create_update'),
    path('vehicles/cert_vehicle/<int:pk>/', CertVehicleDeleteAPI.as_view(), name='api_cert_vehicle_delete'),
    path('vehicles/pass_vehicle/', PassVehicleCreateUpdateAPI.as_view(), name='api_pass_vehicle_create_update'),
    path('vehicles/pass_vehicle/<int:pk>/', PassVehicleDeleteAPI.as_view(), name='api_pass_vehicle_delete'),
	path('vehicles/avaliables/', GetVehiclesAvaliablesAPI.as_view(), name='api_get_vehicles_avaliables'),
    # technicals
    path('technicals/create_update_pass_technical/', CreateUpdatePassTechnicalAPI.as_view(), name='api_create_update_pass_technical'),
    path('technicals/create_update_vaccine/', CreateUpdateVaccineAPI.as_view(), name='api_create_update_vaccine'),
    path('technicals/delete_pass_technical/', DeletePassTechnicalAPI.as_view(), name='api_delete_pass_technical'),
    path('technicals/delete_vaccine/', DeleteVaccineAPI.as_view(), name='api_delete_vaccine'),
    path('technicals/avaliables/', GetTechnicalsAvaliablesAPI.as_view(), name='api_get_technicals_avaliables'),
    # resources
    path('resources/update/', UpdateResourceAPI.as_view(), name='api_update_resource'),
    # projects
	path('projects/data/<int:project_id>/', ProjectData.as_view(), name='api_project_data'),
    path('projects/resources/available/', ResourcesAvailableAPI.as_view(), name='api_resources_available'),
    path('projects/resources/add/', AddResourceProjectAPI.as_view(), name='api_add_resource_project'),
	path('projects/resources/update/', UpdateResourceItemAPI.as_view(), name='api_update_resource_item'),
    path('projects/resources/delete/<int:id_project_resource>/', DeleteResourceProjectAPI.as_view(), name='api_delete_resource_project'),
    path('projects/<int:project_id>/resources/', ProjectResources.as_view(), name='api_project_resources'),    
    
    # workorders
    path('workorders/sheets/project/<int:project_id>/', GetAllSheetProjectAPI.as_view(), name='api_get_all_sheets'),
    path('workorders/sheets/create/', AddUpdateSheetProjectAPI.as_view(), name='api_create_sheet'),
    path('workorders/sheets/delete/', DeleteSheetOrderAPI.as_view(), name='api_delete_sheet'),
    path('workorders/sheets/items/<int:sheet_project_id>/', GetAllSheerProjectItemsAPI.as_view(), name='api_get_all_sheet_project_items'),
    path('workorders/custody_chain/create/', CreateCustodyChainAPI.as_view(), name='api_create_custody_chain'),
]

