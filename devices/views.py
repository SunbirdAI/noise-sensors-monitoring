from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from .models import Device, Location
from .serializers import DeviceConfigSerializer
from rest_framework import viewsets

from .forms import DeviceForm, DeviceConfigurationForm


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

class LocationCreateView(CreateView):
    model = Location
    fields = '__all__'
    success_url = '/devices/'
    template_name = 'devices/update_location.html'


class LocationUpdateView(UpdateView):
    model = Location
    fields = ['latitude', 'longitude', 'city', 'place_name']
    success_url = '/devices/'
    template_name = 'devices/update_location.html'


class DeviceConfigurationUpdateView(UpdateView):
    model = Device
    form_class = DeviceConfigurationForm
    template_name = 'devices/edit_configuration.html'

    def get_success_url(self):
        return reverse('device_detail', kwargs={'pk': self.object.pk})


class DeviceConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceConfigSerializer
    queryset = Device.objects.all()
    lookup_field = 'imei'
