from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (  # DailyAnalysisView,; ReceiveIoTDataView,
    AggregateMetricsView,
    HourlyAnalysisView,
    ListMetricsFilesView,
    ReceiveMetricsFileViewSet,
)

router = SimpleRouter()
router.register("metrics-file", ReceiveMetricsFileViewSet)

# urlpatterns = [
#     path('hourly/', HourlyAnalysisView.as_view(), name='hourly_analysis'),
#     path('daily/', DailyAnalysisView.as_view(), name='daily_analysis'),
#     path('receive_iot_data/', ReceiveIoTDataView.as_view(), name='iot_data'),
# ]
urlpatterns = [
    path(
        "aggregate-metrics/", AggregateMetricsView.as_view(), name="aggregate_metrics"
    ),
    path(
        "list-metrics/<str:device_id>",
        ListMetricsFilesView.as_view(),
        name="list_metric_files",
    ),
    path(
        "hourly/<str:device_id>", HourlyAnalysisView.as_view(), name="hourly_analysis"
    ),
    path("", include(router.urls)),
]
