from django.urls import path, include

from .views import (
    DeviceListView, DeviceDetailView, DeviceCreateView, DeviceUpdateView,
    DeviceConfigurationUpdateView, DeviceConfigurationViewSet,
    LocationViewSet, LocationUpdateView
)

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('config', DeviceConfigurationViewSet)
router.register('location', LocationViewSet)

urlpatterns = [
    path('', DeviceListView.as_view(), name='device_list'),
    path('<uuid:pk>', DeviceDetailView.as_view(), name='device_detail'),
    path('create_device/', DeviceCreateView.as_view(), name='create_device'),
    path('<uuid:pk>/edit/', DeviceUpdateView.as_view(), name='edit_device'),
    path('<uuid:pk>/config_edit', DeviceConfigurationUpdateView.as_view(), name='edit_config'),
    path('<uuid:pk>/location_edit', LocationUpdateView.as_view(), name='edit_location'),
    path('', include(router.urls))
]
