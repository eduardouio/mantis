from django.urls import path
from reports.views.CustodyChain import CustodyChainReportView
from reports.views.PDFCustodyChain import PDFCustodyChain
from reports.views.TechnicalInformationReport import TechnicalInformationReport

app_name = 'reports'

urlpatterns = [
    path('reports/template-custody-chain/<int:id_custody_chain>/', CustodyChainReportView.as_view(), name='custody-chain-report'),
    path('reports/custody-chain/<int:id_custody_chain>/', PDFCustodyChain.as_view(), name='custody-chain-pdf'),
    path('reports/technical/<int:id>/', TechnicalInformationReport.as_view(), name='technical-information-report'),
]
