from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from recordings.models import Recording

from .forms import DeviceConfigurationForm, DeviceForm
from .models import Device, Location
from .serializers import (
    DeviceConfigSerializer,
    DeviceLocationSerializer,
    LocationMetricsSerializer,
    LocationRecordingsSerializer,
    RecordingSerializer,
)
from .uptime_calculation import calculate_uptime


class DeviceLocationListAPIView(ListAPIView):
    queryset = Location.objects.all()
    serializer_class = DeviceLocationSerializer


class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    context_object_name = "device_list"
    template_name = "devices/device_list.html"


class LocationMetricsViewSet(viewsets.ModelViewSet):
    serializer_class = LocationMetricsSerializer
    queryset = Location.objects.all()
    lookup_field = "device"


class LocationRecordingsViewSet(viewsets.ModelViewSet):
    serializer_class = LocationRecordingsSerializer
    queryset = Location.objects.all()
    lookup_field = "id"


class DeviceDetailView(LoginRequiredMixin, DetailView):
    model = Device
    context_object_name = "device"
    template_name = "devices/device_detail.html"


class DeviceCreateView(LoginRequiredMixin, CreateView):
    model = Device
    form_class = DeviceForm
    success_url = "/devices/"
    template_name = "devices/create_device.html"


class DeviceUpdateView(LoginRequiredMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    success_url = "/devices/"
    template_name = "devices/edit_device.html"


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    fields = "__all__"
    success_url = "/devices/"
    template_name = "devices/update_location.html"


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    fields = [
        "latitude",
        "longitude",
        "city",
        "division",
        "parish",
        "village",
        "category",
    ]
    success_url = "/devices/"
    template_name = "devices/update_location.html"


class DeviceConfigurationUpdateView(LoginRequiredMixin, UpdateView):
    model = Device
    form_class = DeviceConfigurationForm
    template_name = "devices/edit_configuration.html"

    def get_success_url(self):
        return reverse("device_detail", kwargs={"pk": self.object.pk})


class DeviceConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceConfigSerializer
    queryset = Device.objects.all()
    lookup_field = "imei"


class UptimeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        device_id = self.kwargs["device_id"]
        past_weeks = int(request.query_params.get("past_weeks", 4))

        # Assuming you have a Device model, fetch the device object
        device = get_object_or_404(Device, device_id=device_id)

        # Call the calculate_uptime function with the device object
        uptime_based_on_audio_uploads = calculate_uptime(device, past_weeks, audio=True)
        uptime_based_on_metrics_uploads = calculate_uptime(
            device, past_weeks, audio=False
        )

        context = {
            "device": device,  # Add the device to the context if needed in the template
            "uptime_based_on_audio_uploads": uptime_based_on_audio_uploads,
            "uptime_based_on_metrics_uploads": uptime_based_on_metrics_uploads,
        }

        return TemplateResponse(request, "devices/device_detail.html", context)


class DeviceRecordingsAPIView(APIView):
    def get(self, request, pk):
        try:
            device = Device.objects.get(pk=pk)
            recordings = device.get_recordings
            # Assuming you have a serializer for Recording model
            serializer = RecordingSerializer(recordings, many=True)
            return Response(serializer.data, status=200)
        except Device.DoesNotExist:
            return Response({"error": "Device not found"}, status=404)
