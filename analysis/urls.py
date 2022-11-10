from django.urls import path
from .views import (
    AnalysisView,
    ReceiveHourlyDataView,
    ReceiveDailyDataView
)

urlpatterns = [
    path('', AnalysisView.as_view(), name='analysis'),
    path('hourly_data/', ReceiveHourlyDataView.as_view(), name='hourly'),
    path('daily_data/', ReceiveDailyDataView.as_view(), name='daily')
]
