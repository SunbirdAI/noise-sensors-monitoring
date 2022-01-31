from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView

from .models import DeviceMetrics
from .serializers import DeviceMetricsSerializer


class DeviceMetricsListCreateView(ListCreateAPIView):
    queryset = DeviceMetrics.objects.all()
    serializer_class = DeviceMetricsSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = DeviceMetricsSerializer(queryset, many=True)
        return Response(serializer.data)


class ReceiveDeviceMetricsViewSet(viewsets.ModelViewSet):
    queryset = DeviceMetrics.objects.all()
    serializer_class = DeviceMetricsSerializer
    http_method_names = ['get', 'post']
