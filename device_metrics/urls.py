from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    DeviceMetricsByDeviceIdAggregateView,
    DeviceMetricsByDeviceIdHistoryView,
    EnvironmentalParameterViewSet,
    ListDeviceMetrics,
    ReceiveDeviceMetricsViewSet,
    SoundInferenceDataViewSet,
)

router = SimpleRouter()
router.register(r"devices", ReceiveDeviceMetricsViewSet)
router.register(r"environmental-parameters", EnvironmentalParameterViewSet)
router.register(r"sound-inference-data", SoundInferenceDataViewSet)

urlpatterns = [
    path(
        "device/by-device-id/<str:device_id>/history/",
        DeviceMetricsByDeviceIdHistoryView.as_view(),
        name="device_metrics_by_device_id_history",
    ),
    path(
        "device/by-device-id/<str:device_id>/aggregates/",
        DeviceMetricsByDeviceIdAggregateView.as_view(),
        name="device_metrics_by_device_id_aggregates",
    ),
    path(
        "device/<uuid:pk>/",
        ListDeviceMetrics.as_view(),
        name="device_device_metrics",
    ),
    path("", include(router.urls)),
]
