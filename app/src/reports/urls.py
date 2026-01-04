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

app_name = 'reports'

urlpatterns = [
	
	# Template URLs
    path('reports/template-custody-chain/<int:id_custody_chain>/', CustodyChainReportView.as_view(), name='custody-chain-report'),
    path('reports/template-technical/<int:id>/', TechnicalInformationReport.as_view(), name='technical-information-report'),
    path('reports/template-technical-vaccine/<int:id>/', TechnicalVaccineReport.as_view(), name='technical-vaccine-report'),
    
    # Equipment Checklists Templates
    path('reports/template-equipment-bateries/<int:equipment_id>/', EquipmentBateriesCheckList.as_view(), name='equipment-bateries-checklist'),
    path('reports/template-equipment-washer-hands/<int:equipment_id>/', EquipmentWasherHandsCheck.as_view(), name='equipment-washer-hands-checklist'),
    path('reports/template-equipment-urinal-station/<int:equipment_id>/', EquipmentUrinalStationCheck.as_view(), name='equipment-urinal-station-checklist'),
    path('reports/template-equipment-bathroom-camper/<int:equipment_id>/', EquipmentBathroomCamperChecker.as_view(), name='equipment-bathroom-camper-checklist'),
    path('reports/template-equipment-raw-water-tanks/<int:equipment_id>/', EquipmentRawWaterStorageTanks.as_view(), name='equipment-raw-water-tanks-checklist'),
    path('reports/template-equipment-wastewater-tanks/<int:equipment_id>/', EquipmentWastewaterStorageTanks.as_view(), name='equipment-wastewater-tanks-checklist'),
	
    # PDF URLs
    path('reports/custody-chain/<int:id_custody_chain>/', PDFCustodyChain.as_view(), name='custody-chain-pdf'),
    path('reports/technical/<int:id>/', PDFTechnicalInformation.as_view(), name='technical-information-pdf'),
    path('reports/technical-vaccine/<int:id>/', PDFTechnicalVaccineReport.as_view(), name='technical-vaccine-pdf'),
]
