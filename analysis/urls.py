from django.urls import path, include
from .views import (
    # HourlyAnalysisView,
    # DailyAnalysisView,
    # ReceiveIoTDataView,
    ReceiveMetricsFileViewSet
)
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('metrics-file', ReceiveMetricsFileViewSet)

# urlpatterns = [
#     path('hourly/', HourlyAnalysisView.as_view(), name='hourly_analysis'),
#     path('daily/', DailyAnalysisView.as_view(), name='daily_analysis'),
#     path('receive_iot_data/', ReceiveIoTDataView.as_view(), name='iot_data'),
# ]
urlpatterns = [
    path('', include(router.urls))
]
