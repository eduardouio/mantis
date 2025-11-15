from django.urls import path
from reports.views.CustodyChain import CustodyChainReportView
from reports.views.PDFCustodyChain import PDFCustodyChain
from reports.views.TechnicalInformationReport import TechnicalInformationReport
from reports.views.PDFTechnicalInformation import PDFTechnicalInformation
from reports.views.TechnicalVaccineReport import TechnicalVaccineReport
from reports.views.PDFTechnicalVaccineReport import PDFTechnicalVaccineReport

app_name = 'reports'

urlpatterns = [
	
	# Template URLs
    path('reports/template-custody-chain/<int:id_custody_chain>/', CustodyChainReportView.as_view(), name='custody-chain-report'),
    path('reports/template-technical/<int:id>/', TechnicalInformationReport.as_view(), name='technical-information-report'),
    path('reports/template-technical-vaccine/<int:id>/', TechnicalVaccineReport.as_view(), name='technical-vaccine-report'),
	
    # PDF URLs
    path('reports/custody-chain/<int:id_custody_chain>/', PDFCustodyChain.as_view(), name='custody-chain-pdf'),
    path('reports/technical/<int:id>/', PDFTechnicalInformation.as_view(), name='technical-information-pdf'),
    path('reports/technical-vaccine/<int:id>/', PDFTechnicalVaccineReport.as_view(), name='technical-vaccine-pdf'),
]
