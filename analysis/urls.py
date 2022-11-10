from django.urls import path
from .views import (
    AnalysisView,
    ReceiveIoTDataView
)

urlpatterns = [
    path('', AnalysisView.as_view(), name='analysis'),
    path('receive_iot_data/', ReceiveIoTDataView.as_view(), name='iot_data'),
]
