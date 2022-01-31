from django.urls import path, include

from .views import ReceiveDeviceMetricsViewSet, ListDeviceMetrics

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', ReceiveDeviceMetricsViewSet)

urlpatterns = [
    path('<slug:device_id>', ListDeviceMetrics.as_view(), name='device_device_metrics'),
    path('', include(router.urls))
]