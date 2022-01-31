from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView

from .models import DeviceMetrics
from .serializers import DeviceMetricsSerializer


class ReceiveDeviceMetricsViewSet(viewsets.ModelViewSet):
    queryset = DeviceMetrics.objects.all()
    serializer_class = DeviceMetricsSerializer
    http_method_names = ['get', 'post']
