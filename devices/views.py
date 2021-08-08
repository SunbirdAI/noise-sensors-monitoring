from django.views.generic import ListView, DetailView
from .models import Device


class DeviceListView(ListView):
    model = Device
    context_object_name = 'device_list'
    template_name = 'devices/device_list.html'


class DeviceDetailView(DetailView):
    model = Device
    context_object_name = 'device'
    template_name = 'devices/device_detail.html'
