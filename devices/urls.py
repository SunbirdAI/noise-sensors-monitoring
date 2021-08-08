from django.urls import path

from .views import DeviceListView, DeviceDetailView, DeviceFormView


urlpatterns = [
    path('', DeviceListView.as_view(), name='device_list'),
    path('<uuid:pk>', DeviceDetailView.as_view(), name='device_detail'),
    path('create_device/', DeviceFormView.as_view(), name='create_device')
]
