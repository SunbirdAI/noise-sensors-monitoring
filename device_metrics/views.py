from rest_framework import viewsets
from rest_framework.generics import ListAPIView

from .models import DeviceMetrics, EnvironmentalParameter, SoundInferenceData
from .serializers import (
    DeviceMetricsSerializer,
    EnvironmentalParameterSerializer,
    SoundInferenceDataSerializer,
)


class ReceiveDeviceMetricsViewSet(viewsets.ModelViewSet):
    queryset = DeviceMetrics.objects.all()
    serializer_class = DeviceMetricsSerializer


class ListDeviceMetrics(ListAPIView):
    queryset = DeviceMetrics.objects.all()
    serializer_class = DeviceMetricsSerializer

    def get_queryset(self):
        return self.queryset.filter(device__id=self.kwargs["pk"])


class EnvironmentalParameterViewSet(viewsets.ModelViewSet):
    queryset = EnvironmentalParameter.objects.all().order_by("-created_at")
    serializer_class = EnvironmentalParameterSerializer


class SoundInferenceDataViewSet(viewsets.ModelViewSet):
    queryset = SoundInferenceData.objects.all().order_by("-created_at")
    serializer_class = SoundInferenceDataSerializer
