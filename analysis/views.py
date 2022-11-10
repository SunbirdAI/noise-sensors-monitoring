from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HourlyAggregate, DailyAggregate

from .serializers import ReceiveIoTMetricsSerializer

from .aggregate_iot_data import aggregate_hourly, aggregate_daily

class AnalysisView(APIView):

    def get(self, request):
        pass


class ReceiveIoTDataView(APIView):

    def post(self, request):
        kind = request.data["type"]
        if kind == "hourly":
            aggregation = aggregate_hourly(request.data["data"])
        elif kind == "daytime" or kind == "nighttime":
            aggregation = aggregate_daily(request.data["data"], kind)
        else:
            return Response(
                {"Error": "Invlaid request: Please add a type to the data object"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(aggregation, status=status.HTTP_201_CREATED)
