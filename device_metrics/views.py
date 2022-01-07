from rest_framework import viewsets

from .models import DeviceMetrics
from .serializers import DeviceMetricsFullSerializer


class ReceiveDeviceMetricsViewSet(viewsets.ModelViewSet):
    queryset = DeviceMetrics.objects.all()
    serializer_class = DeviceMetricsFullSerializer
    http_method_names = ['post']
