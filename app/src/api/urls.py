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
from api.projects.CloseProjectAPI import CloseProjectAPI

from api.workorders import (
    GetAllSheetProjectAPI,
    DeleteSheetOrderAPI,
    UpdateSheetOrderAPI,
)

from api.projects.ProjectResources import ProjectResources
from api.workorders.GetAllSheerProjectItems import GetAllSheerProjectItemsAPI
from api.workorders.CreateCustodyChain import CreateCustodyChainAPI
from api.projects.UpdateResourceItem import UpdateResourceItemAPI
from api.vehicles.GetVehiclesAvaliablesAPI import GetVehiclesAvaliablesAPI
from api.technicals.GetTechnicalsAvaliablesAPI import GetTechnicalsAvaliablesAPI
from api.workorders.CustodyChainDetailAPI import CustodyChainDetailAPI
from api.workorders.AllInfoProjectAPI import AllInfoProjectAPI
from api.workorders.CustodyChainEditAPI import CustodyChainEditAPI
from api.workorders.RegenerateEquipmentCodes import RegenerateEquipmentCodesAPI
from api.resources.ResourceReleaserAPI import ResourceReleaserAPI
from api.workorders.CreateWorkSheetProject import CreateWorkSheetProjectAPI
from api.workorders.UpdateSheetProject import UpdateSheetProjectAPI
from api.workorders.UpdateSheetDetailDays import UpdateSheetDetailDaysAPI
from api.workorders.ReopenSheetProject import ReopenSheetProjectAPI
from api.load_files import LoadFilesApiView, ModelFileFieldsApiView, DocumentTreeApiView
from api.load_files import ProjectDocumentTreeApiView, ProjectDocumentMergeApiView, BulkCustodyUploadApiView
from api.load_files.SheetMergeGeneratedApiView import SheetMergeGeneratedApiView
from api.load_files.VehicleMergeGeneratedApiView import VehicleMergeGeneratedApiView
from api.load_files.TechnicalMergeGeneratedApiView import TechnicalMergeGeneratedApiView
from api.shipping import ShippingGuideCreateUpdateAPI, ShippingGuideDeleteAPI
from api.maintenance import SheetMaintenanceCreateUpdateAPI, SheetMaintenanceDeleteAPI
from api.calendar import CalendarEventCreateUpdateAPI, CalendarEventDeleteAPI

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
    path('projects/resources/available/', ResourcesAvailableAPI.as_view(), name='api_resources_available'),
    path('projects/resources/add/', AddResourceProjectAPI.as_view(), name='api_add_resource_project'),
    path('projects/resources/update/', UpdateResourceItemAPI.as_view(), name='api_update_resource_item'),
    path('projects/resources/delete/<int:id_project_resource>/', DeleteResourceProjectAPI.as_view(), name='api_delete_resource_project'),
	path('projects/resources/release/', ResourceReleaserAPI.as_view(), name='api_release_resource_project'),
    path('projects/<int:project_id>/resources/', ProjectResources.as_view(), name='api_project_resources'),
    path('projects/all-info/<int:project_id>/', AllInfoProjectAPI.as_view(), name='api_all_info_project'),
    path('projects/<int:project_id>/close/', CloseProjectAPI.as_view(), name='api_close_project'),
    
    # workorders
    path('workorders/sheets/project/<int:project_id>/', GetAllSheetProjectAPI.as_view(), name='api_get_all_sheets'),
    path('workorders/sheets/create/', CreateWorkSheetProjectAPI.as_view(), name='api_create_sheet'),
    path('workorders/sheets/update/', UpdateSheetProjectAPI.as_view(), name='api_update_sheet'),
    path('workorders/sheets/delete/', DeleteSheetOrderAPI.as_view(), name='api_delete_sheet'),
    path('workorders/sheets/detail/<int:detail_id>/days/', UpdateSheetDetailDaysAPI.as_view(), name='api_update_sheet_detail_days'),
    path('workorders/sheets/reopen/', ReopenSheetProjectAPI.as_view(), name='api_reopen_sheet'),
	
    path('workorders/sheets/items/<int:sheet_project_id>/', GetAllSheerProjectItemsAPI.as_view(), name='api_get_all_sheet_project_items'),
    path('workorders/custody_chain/create/', CreateCustodyChainAPI.as_view(), name='api_create_custody_chain'),
    path('workorders/custody_chain/detail/<int:id>/', CustodyChainDetailAPI.as_view(), name='api_custody_chain_detail'),
    path('workorders/custody_chain/<int:id>/edit/', CustodyChainEditAPI.as_view(), name='api_edit_custody_chain'),
    path('workorders/custody_chain/regenerate-codes/', RegenerateEquipmentCodesAPI.as_view(), name='api_regenerate_equipment_codes'),

    # load_files - API centralizada de archivos
    path('load_files/', LoadFilesApiView.as_view(), name='api_load_files'),
    path('load_files/fields/', ModelFileFieldsApiView.as_view(), name='api_load_files_fields'),
    path('load_files/tree/', DocumentTreeApiView.as_view(), name='api_load_files_tree'),
    path('load_files/project/<int:project_id>/tree/', ProjectDocumentTreeApiView.as_view(), name='api_project_document_tree'),
    path('load_files/project/<int:project_id>/merge/', ProjectDocumentMergeApiView.as_view(), name='api_project_document_merge'),
    path('load_files/project/<int:project_id>/bulk_custody/', BulkCustodyUploadApiView.as_view(), name='api_bulk_custody_upload'),
    path('load_files/sheet/<int:sheet_id>/merge-generated/', SheetMergeGeneratedApiView.as_view(), name='api_sheet_merge_generated'),
    path('load_files/vehicle/<int:vehicle_id>/merge-generated/', VehicleMergeGeneratedApiView.as_view(), name='api_vehicle_merge_generated'),
    path('load_files/technical/<int:technical_id>/merge-generated/', TechnicalMergeGeneratedApiView.as_view(), name='api_technical_merge_generated'),

    # shipping guides
    path('shipping/guides/', ShippingGuideCreateUpdateAPI.as_view(), name='api_shipping_guide_create_update'),
    path('shipping/guides/<int:guide_id>/', ShippingGuideCreateUpdateAPI.as_view(), name='api_shipping_guide_detail'),
    path('shipping/guides/<int:pk>/delete/', ShippingGuideDeleteAPI.as_view(), name='api_shipping_guide_delete'),

    # maintenance sheets
    path('maintenance/sheets/', SheetMaintenanceCreateUpdateAPI.as_view(), name='api_maintenance_sheet_create_update'),
    path('maintenance/sheets/<int:sheet_id>/', SheetMaintenanceCreateUpdateAPI.as_view(), name='api_maintenance_sheet_detail'),
    path('maintenance/sheets/<int:pk>/delete/', SheetMaintenanceDeleteAPI.as_view(), name='api_maintenance_sheet_delete'),

    # calendar events
    path('calendar/events/', CalendarEventCreateUpdateAPI.as_view(), name='api_calendar_events'),
    path('calendar/events/<int:event_id>/', CalendarEventCreateUpdateAPI.as_view(), name='api_calendar_event_detail'),
    path('calendar/events/<int:event_id>/move/', CalendarEventCreateUpdateAPI.as_view(), name='api_calendar_event_move'),
    path('calendar/events/<int:pk>/delete/', CalendarEventDeleteAPI.as_view(), name='api_calendar_event_delete'),
]