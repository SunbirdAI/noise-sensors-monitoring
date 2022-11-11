from django.urls import path
from .views import (
    HourlyAnalysisView,
    DailyAnalysisView,
    ReceiveIoTDataView
)

urlpatterns = [
    path('hourly/', HourlyAnalysisView.as_view(), name='hourly_analysis'),
    path('daily/', DailyAnalysisView.as_view(), name='daily_analysis'),
    path('receive_iot_data/', ReceiveIoTDataView.as_view(), name='iot_data'),
]
