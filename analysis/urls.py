from django.urls import path
from .views import (
    AnalysisView,
    HourlyAggregateCreateView,
    DailyAggregateCreateView
)

urlpatterns = [
    path('', AnalysisView.as_view(), name='analysis'),
    path('aggregates/', HourlyAggregateCreateView.as_view(), name='hourly'),
    path('daily_aggregates/', DailyAggregateCreateView.as_view(), name='daily')
]
