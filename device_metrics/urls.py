from django.urls import path, include

from .views import ReceiveDeviceMetricsViewSet, DeviceMetricsListCreateView

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', ReceiveDeviceMetricsViewSet)

urlpatterns = [
    path('', DeviceMetricsListCreateView.as_view(), name='device_metrics_list'),
    path('metrics/', include(router.urls))
]