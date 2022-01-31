from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from .models import DeviceMetrics
from .serializers import DeviceMetricsSerializer


class ReceiveDeviceMetricsViewSet(viewsets.ModelViewSet):
    queryset = DeviceMetrics.objects.all()
    serializer_class = DeviceMetricsSerializer


class ListDeviceMetrics(ListAPIView):
    queryset = DeviceMetrics.objects.all()
    serializer_class = DeviceMetricsSerializer

    def get_queryset(self):
        return self.queryset.filter(
            device__device_id=self.kwargs['device_id']
        )
