from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from .models import Device

from .forms import DeviceForm


class DeviceListView(ListView):
    model = Device
    context_object_name = 'device_list'
    template_name = 'devices/device_list.html'


class DeviceDetailView(DetailView):
    model = Device
    context_object_name = 'device'
    template_name = 'devices/device_detail.html'


class DeviceCreateView(CreateView):
    model = Device
    form_class = DeviceForm
    success_url = '/devices/'
    template_name = 'devices/create_device.html'


class DeviceUpdateView(UpdateView):
    model = Device
    form_class = DeviceForm
    success_url = '/devices/'
    template_name = 'devices/edit_device.html'
