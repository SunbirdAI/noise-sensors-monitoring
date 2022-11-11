import pytz

from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from .models import HourlyAggregate, DailyAggregate

from .serializers import (
    HourlyAnalysisSerializer, DailyAnalysisSerializer
)

from .aggregate_iot_data import Aggregate

from noise_dashboard.settings import TIME_ZONE


timezone = pytz.timezone(TIME_ZONE)
today = datetime.today()
today = timezone.localize(today)


class HourlyAnalysisView(ListAPIView):
    today = datetime.today()
    queryset = HourlyAggregate.objects.filter(
        date__year=today.year,
        date__month=today.month,
        date__day=today.day
    )
    # queryset = HourlyAggregate.objects.all()
    serializer_class = HourlyAnalysisSerializer


class DailyAnalysisView(ListAPIView):
    today = datetime.today()
    queryset = DailyAggregate.objects.filter(
        date__year=today.year,
        date__month=today.month,
        date__day=today.day
    )
    # queryset = DailyAggregate.objects.all()
    serializer_class = DailyAnalysisSerializer


class ReceiveIoTDataView(APIView):

    def post(self, request):
        time_period = request.data["type"]
        agg = Aggregate(request.data["data"])
        if time_period == "hourly":
            agg.aggregate_hourly()
        elif time_period == "daytime" or time_period == "nighttime":
            agg.aggregate_daily(time_period)
        else:
            return Response(
                {"Error": "Invalid request: Please add a proper type (hourly, daytime or nighttime) to the data object"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response("Success", status=status.HTTP_201_CREATED)
