import pytz

from datetime import datetime, timedelta

from rest_framework import viewsets, parsers
from rest_framework.response import Response
from rest_framework.views import APIView
from .aggregate_data import Aggregate

from .models import MetricsTextFile

from .serializers import (
    UploadMetricsTextFileSerializer
)

from devices.models import Device
from .parse_file_metrics import parse_file

from noise_dashboard.settings import TIME_ZONE

timezone = pytz.timezone(TIME_ZONE)
today = datetime.today()
today = timezone.localize(today)
four_weeks = timedelta(weeks=4)


class ReceiveMetricsFileViewSet(viewsets.ModelViewSet):
    queryset = MetricsTextFile.objects.all()
    serializer_class = UploadMetricsTextFileSerializer
    parser_classes = [parsers.MultiPartParser]
    http_method_names = ['post']


class AggregateMetricsView(APIView):

    def post(self, request):
        device_id = request.data["device_id"]
        start = int(request.data["start"])
        end = int(request.data["end"])
        start_days = timedelta(days=start)
        end_days = timedelta(days=end)
        device = Device.objects.get(device_id=device_id)
        metric_files = device.metricstextfile_set.all()
        processed_files = []
        for metric_file in metric_files:
            if not ((today - end_days) <= metric_file.time_uploaded <= (today - start_days)):
                continue
            metrics_data = parse_file(metric_file.metrics_file.file, device_id)
            if len(metrics_data) == 0:
                continue
            agg = Aggregate(metrics_data)
            agg.aggregate_hourly(time_uploaded=metric_file.time_uploaded)
            processed_files.append(metric_file)
        metric_files_dict = {
            "number_of_files": len(processed_files),
            "files": [
                {'time_uploaded': metric_file.time_uploaded,
                 'device': metric_file.device.device_id,
                 'filename': metric_file.filename
                 } for metric_file in processed_files
            ]
        }
        return Response(metric_files_dict)

#
# class HourlyAnalysisView(ListAPIView):
#     # today = datetime.today()
#     # queryset = HourlyAggregate.objects.filter(
#     #     date__year=today.year,
#     #     date__month=today.month,
#     #     date__day=today.day
#     # )
#     queryset = HourlyAggregate.objects.all()
#     serializer_class = HourlyAnalysisSerializer
#
#
# class DailyAnalysisView(ListAPIView):
#     # today = datetime.today()
#     # queryset = DailyAggregate.objects.filter(
#     #     date__year=today.year,
#     #     date__month=today.month,
#     #     date__day=today.day
#     # )
#     queryset = DailyAggregate.objects.all()
#     serializer_class = DailyAnalysisSerializer
#
#
# class ReceiveIoTDataView(APIView):
#
#     def post(self, request):
#         time_period = request.data["type"]
#         agg = Aggregate(request.data["data"])
#         if time_period == "hourly":
#             agg.aggregate_hourly()
#         elif time_period == "daytime" or time_period == "nighttime":
#             agg.aggregate_daily(time_period)
#         else:
#             return Response(
#                 {"Error": "Invalid request: Please add a proper type (hourly, daytime or nighttime) to the data object"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         return Response("Success", status=status.HTTP_201_CREATED)
