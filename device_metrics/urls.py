from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
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
    path("device/<uuid:pk>", ListDeviceMetrics.as_view(), name="device_device_metrics"),
    path("", include(router.urls)),
]
