import pytz

from datetime import datetime, timedelta

from rest_framework import viewsets, parsers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .aggregate_data import Aggregate

from .models import MetricsTextFile, HourlyAggregate

from .serializers import (
    UploadMetricsTextFileSerializer,
    ListMetricsTextFileSerializer,
    HourlyAnalysisSerializer
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


class ListMetricsFilesView(ListAPIView):
    serializer_class = ListMetricsTextFileSerializer

    def list(self, request, *args, **kwargs):
        past_days = request.query_params.get('past_days', 1)
        queryset = self.get_queryset(int(past_days))
        serializer = self.get_serializer(queryset, many=True)
        num_files = len(serializer.data)
        result = {
            "number_of_files": num_files,
            "metric_files": serializer.data
        }
        return Response(result)

    def get_queryset(self, past_days=1):
        device_id = self.kwargs['device_id']
        queryset = MetricsTextFile.objects.filter(device__device_id=device_id)
        queryset = queryset.filter(time_uploaded__range=[today - timedelta(days=past_days), today])
        return queryset.order_by('-time_uploaded')


class AggregateMetricsView(APIView):

    def post(self, request):
        device_id = request.data["device_id"]
        start = int(request.data["start"])
        end = int(request.data["end"])
        start_days = timedelta(days=start)
        end_days = timedelta(days=end)
        device = Device.objects.get(device_id=device_id)
        metric_files = device.metricstextfile_set.filter(time_uploaded__range=[today - end_days, today - start_days])
        processed_files = []
        for metric_file in metric_files:
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
class HourlyAnalysisView(ListAPIView):
    serializer_class = HourlyAnalysisSerializer

    def get_queryset(self):
        device_id = self.kwargs["device_id"]
        past_days = int(self.request.query_params.get('past_days', 1))
        queryset = HourlyAggregate.objects.filter(device__device_id=device_id)
        queryset = queryset.filter(date__range=[today - timedelta(past_days), today])
        return queryset.order_by('-date')

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
