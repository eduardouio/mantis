from django.urls import path
from reports.views.CustodyChain import CustodyChainReportView
from reports.views.PDFCustodyChain import PDFCustodyChain
from reports.views.TechnicalInformationReport import TechnicalInformationReport
from reports.views.PDFTechnicalInformation import PDFTechnicalInformation
from reports.views.TechnicalVaccineReport import TechnicalVaccineReport
from reports.views.PDFTechnicalVaccineReport import PDFTechnicalVaccineReport
from reports.views.EquipmentBateriesCheckList import EquipmentBateriesCheckList
from reports.views.EquipmentWasherHandsCheck import EquipmentWasherHandsCheck
from reports.views.EquipmentUrinalStationCheck import EquipmentUrinalStationCheck
from reports.views.EquipmentBathroomCamperChecker import EquipmentBathroomCamperChecker
from reports.views.EquipmentRawWaterStorageTanks import EquipmentRawWaterStorageTanks
from reports.views.EquipmentWastewaterStorageTanks import EquipmentWastewaterStorageTanks
from reports.views.EquipmentInfoReport import EquipmentInfoReport
from reports.views.PDFBateriesCheckList import PDFBateriesCheckList
from reports.views.PDFWasherHandsCheck import PDFWasherHandsCheck
from reports.views.PDFUrinalStationCheck import PDFUrinalStationCheck
from reports.views.PDFBathroomCamperChecker import PDFBathroomCamperChecker
from reports.views.PDFRawWaterStorageTanks import PDFRawWaterStorageTanks
from reports.views.PDFWastewaterStorageTanks import PDFWastewaterStorageTanks
from reports.views.PDFEquipmentInfoReport import PDFEquipmentInfoReport
from reports.views.VehicleStatusReport import VehicleStatusReport
from reports.views.PDFVehicleStatusReport import PDFVehicleStatusReport
from reports.views.ResourcesByStatus import ResourcesByStatusView
from reports.views.VehiclesByStatus import VehiclesByStatusView
from reports.views.TechnicalByStatus import TechnicalByStatusView
from reports.views.WorkSheetTemplateView import WorkSheetTemplateView
from reports.views.PDFWorkSheet import PDFWorkSheet
from reports.views.FinalDispositionCertificate import FinalDispositionCertificateView
from reports.views.PDFFinalDispositionCertificateView import PDFFinalDispositionCertificateView


app_name = 'reports'

urlpatterns = [
	
	# Template URLs
    path('reports/template-custody-chain/<int:id_custody_chain>/', CustodyChainReportView.as_view(), name='custody-chain-report'),
    path('reports/template-technical/<int:id>/', TechnicalInformationReport.as_view(), name='technical-information-report'),
    path('reports/template-technical-vaccine/<int:id>/', TechnicalVaccineReport.as_view(), name='technical-vaccine-report'),
    path('reports/template-equipment-info/<int:equipment_id>/', EquipmentInfoReport.as_view(), name='equipment-info-report'),
    path('reports/template-vehicle-status/<int:pk>/', VehicleStatusReport.as_view(), name='vehicle-status-report'),
    path('reports/equipment-status/', ResourcesByStatusView.as_view(), name='equipment-status-report'),
    path('reports/technicals-status/', TechnicalByStatusView.as_view(), name='technicals-status-report'),
    path('reports/vehicles-status/', VehiclesByStatusView.as_view(), name='vehicles-status-report'),
    path('reports/template-worksheet/<int:id>/', WorkSheetTemplateView.as_view(), name='worksheet-template'),
    path('reports/template-final-disposition/', FinalDispositionCertificateView.as_view(), name='final-disposition-certificate'),

    # Equipment Checklists Templates
    path('reports/template-equipment-bateries/<int:equipment_id>/', EquipmentBateriesCheckList.as_view(), name='equipment-bateries-checklist'),
    path('reports/template-equipment-washer-hands/<int:equipment_id>/', EquipmentWasherHandsCheck.as_view(), name='equipment-washer-hands-checklist'),
    path('reports/template-equipment-urinal-station/<int:equipment_id>/', EquipmentUrinalStationCheck.as_view(), name='equipment-urinal-station-checklist'),
    path('reports/template-equipment-bathroom-camper/<int:equipment_id>/', EquipmentBathroomCamperChecker.as_view(), name='equipment-bathroom-camper-checklist'),
    path('reports/template-equipment-raw-water-tanks/<int:equipment_id>/', EquipmentRawWaterStorageTanks.as_view(), name='equipment-raw-water-tanks-checklist'),
    path('reports/template-equipment-wastewater-tanks/<int:equipment_id>/', EquipmentWastewaterStorageTanks.as_view(), name='equipment-wastewater-tanks-checklist'),
	
    # PDF URLs
	path('reports/final-disposition/', PDFFinalDispositionCertificateView.as_view(), name='final-disposition-pdf'),
    path('reports/custody-chain/<int:id_custody_chain>/', PDFCustodyChain.as_view(), name='custody-chain-pdf'),
    path('reports/technical/<int:id>/', PDFTechnicalInformation.as_view(), name='technical-information-pdf'),
    path('reports/technical-vaccine/<int:id>/', PDFTechnicalVaccineReport.as_view(), name='technical-vaccine-pdf'),
    path('reports/equipment-info/<int:equipment_id>/', PDFEquipmentInfoReport.as_view(), name='equipment-info-pdf'),
    path('reports/vehicle-status/<int:pk>/', PDFVehicleStatusReport.as_view(), name='vehicle-status-pdf'),
    path('reports/worksheet/<int:id>/', PDFWorkSheet.as_view(), name='worksheet-pdf'),
    
    # Equipment Checklists PDF
    path('reports/equipment-bateries/<int:equipment_id>/', PDFBateriesCheckList.as_view(), name='equipment-bateries-pdf'),
    path('reports/equipment-washer-hands/<int:equipment_id>/', PDFWasherHandsCheck.as_view(), name='equipment-washer-hands-pdf'),
    path('reports/equipment-urinal-station/<int:equipment_id>/', PDFUrinalStationCheck.as_view(), name='equipment-urinal-station-pdf'),
    path('reports/equipment-bathroom-camper/<int:equipment_id>/', PDFBathroomCamperChecker.as_view(), name='equipment-bathroom-camper-pdf'),
    path('reports/equipment-raw-water-tanks/<int:equipment_id>/', PDFRawWaterStorageTanks.as_view(), name='equipment-raw-water-tanks-pdf'),
    path('reports/equipment-wastewater-tanks/<int:equipment_id>/', PDFWastewaterStorageTanks.as_view(), name='equipment-wastewater-tanks-pdf'),
    
]
