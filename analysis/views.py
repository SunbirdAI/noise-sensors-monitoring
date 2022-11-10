from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HourlyAggregate, DailyAggregate

from .serializers import ReceiveIoTMetricsSerializer

from .aggregate_iot_data import Aggregate

class AnalysisView(APIView):

    def get(self, request):
        pass


class ReceiveIoTDataView(APIView):

    def post(self, request):
        kind_of_data = request.data["type"]
        agg = Aggregate(request.data["data"])
        if kind_of_data == "hourly":
            agg.aggregate_hourly()
        elif kind_of_data == "daytime" or kind_of_data == "nighttime":
            agg.aggregate_daily(kind_of_data)
        else:
            return Response(
                {"Error": "Invalid request: Please add a proper type (hourly, daytime or nighttime) to the data object"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response("Success", status=status.HTTP_201_CREATED)
