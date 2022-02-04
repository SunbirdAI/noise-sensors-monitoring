from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from .models import Device, Location
from .serializers import DeviceConfigSerializer, LocationSerializer
from rest_framework import viewsets

from .forms import DeviceForm, DeviceConfigurationForm, LocationForm


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


class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()


class LocationUpdateView(UpdateView):
    model = Device
    form_class = LocationForm
    template_name = 'devices/edit_location.html'

    def get_success_url(self):
        return reverse('device_detail', kwargs={'pk': self.object.pk})


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
