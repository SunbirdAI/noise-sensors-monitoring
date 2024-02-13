from django.urls import path, include

from .views import (
    DeviceListView, DeviceDetailView, DeviceCreateView, DeviceRecordingsAPIView, DeviceUpdateView,
    DeviceLocationListAPIView, DeviceConfigurationUpdateView,
    DeviceConfigurationViewSet, LocationCreateView, LocationUpdateView,
    LocationMetricsViewSet, LocationRecordingsViewSet, UptimeAPIView
)

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('config', DeviceConfigurationViewSet)
router.register('location_metrics', LocationMetricsViewSet)
router.register('location_recordings', LocationRecordingsViewSet)

urlpatterns = [
    path('', DeviceListView.as_view(), name='device_list'),
    path('locations/', DeviceLocationListAPIView.as_view(), name='device_locations'),
    path('<uuid:pk>', DeviceDetailView.as_view(), name='device_detail'),
    path('create_device/', DeviceCreateView.as_view(), name='create_device'),
    path('<uuid:pk>/edit/', DeviceUpdateView.as_view(), name='edit_device'),
    path('<uuid:pk>/config_edit', DeviceConfigurationUpdateView.as_view(), name='edit_config'),
    path('create_location', LocationCreateView.as_view(), name='create_location'),
    path('<uuid:pk>/edit_location', LocationUpdateView.as_view(), name='edit_location'),
    path('uptime/<str:device_id>', UptimeAPIView.as_view(), name='uptime_info'),
    path('device/<uuid:pk>/recordings/', DeviceRecordingsAPIView.as_view(), name='device_recordings_api'),
    path('', include(router.urls))
]
