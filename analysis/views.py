from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from .models import HourlyAggregate, DailyAggregate
from .serializers import (
    HourlyAggregateSerializer,
    DailyAggregateSerializer
)
from .aggregate_influx_data import InfluxClient

class AnalysisView(APIView):

    def get(self, request):
        client = InfluxClient()
        results = client.aggregate_results()
        return Response(results)


class HourlyAggregateCreateView(CreateAPIView):
    queryset = HourlyAggregate.objects.all()
    serializer_class = HourlyAggregateSerializer


class DailyAggregateCreateView(CreateAPIView):
    queryset = DailyAggregate.objects.all()
    serializer_class = DailyAggregateSerializer
