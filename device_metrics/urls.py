from django.urls import path, include

from .views import DeviceMetricsCreateView, DeviceMetricsListView


urlpatterns = [
    path('', DeviceMetricsListView.as_view(), name='device_metrics_list'),
    path('create_device_metrics/', DeviceMetricsCreateView.as_view(), name='create_device_metrics'),
]
