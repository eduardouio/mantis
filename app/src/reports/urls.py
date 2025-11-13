from django.urls import path
from reports.views.CustodyChain import CustodyChainReportView

app_name = 'reports'

urlpatterns = [
    path('report/custody-chain/', CustodyChainReportView.as_view(), name='custody-chain-report'),
]
