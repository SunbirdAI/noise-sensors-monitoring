from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from .models import Device, Location
from .uptime_calculation import calculate_uptime
from .serializers import (
    DeviceLocationSerializer, DeviceConfigSerializer,
    LocationMetricsSerializer, LocationRecordingsSerializer
    )
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import DeviceForm, DeviceConfigurationForm


class DeviceLocationListAPIView(ListAPIView):
    queryset = Location.objects.all()
    serializer_class = DeviceLocationSerializer


class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    context_object_name = 'device_list'
    template_name = 'devices/device_list.html'


class LocationMetricsViewSet(viewsets.ModelViewSet):
    serializer_class = LocationMetricsSerializer
    queryset = Location.objects.all()
    lookup_field = 'device'


class LocationRecordingsViewSet(viewsets.ModelViewSet):
    serializer_class = LocationRecordingsSerializer
    queryset = Location.objects.all()
    lookup_field = 'id'


class DeviceDetailView(LoginRequiredMixin, DetailView):
    model = Device
    context_object_name = 'device'
    template_name = 'devices/device_detail.html'


class DeviceCreateView(LoginRequiredMixin, CreateView):
    model = Device
    form_class = DeviceForm
    success_url = '/devices/'
    template_name = 'devices/create_device.html'


class DeviceUpdateView(LoginRequiredMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    success_url = '/devices/'
    template_name = 'devices/edit_device.html'

class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    fields = '__all__'
    success_url = '/devices/'
    template_name = 'devices/update_location.html'


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    fields = ['latitude', 'longitude', 'city', 'division', 'parish', 'village', 'category']
    success_url = '/devices/'
    template_name = 'devices/update_location.html'


class DeviceConfigurationUpdateView(LoginRequiredMixin, UpdateView):
    model = Device
    form_class = DeviceConfigurationForm
    template_name = 'devices/edit_configuration.html'

    def get_success_url(self):
        return reverse('device_detail', kwargs={'pk': self.object.pk})


class DeviceConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceConfigSerializer
    queryset = Device.objects.all()
    lookup_field = 'imei'


class UptimeAPIView(APIView):

    def get(self, request, *args, **kwargs):
        device_id = self.kwargs['device_id']
        past_weeks = int(request.query_params.get('past_weeks', 4))
        uptime_based_on_audio_uploads = calculate_uptime(device_id, past_weeks, True)
        uptime_based_on_metrics_uploads = calculate_uptime(device_id, past_weeks, False)
        return Response({
            'uptime_based_on_audio_uploads': uptime_based_on_audio_uploads,
            'uptime_based_on_metrics_uploads': uptime_based_on_metrics_uploads
        })

