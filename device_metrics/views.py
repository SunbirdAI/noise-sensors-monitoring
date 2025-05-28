from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
import csv
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import DeviceMetrics, EnvironmentalParameter, SoundInferenceData
from .serializers import (
    DeviceMetricsSerializer,
    EnvironmentalParameterSerializer,
    SoundInferenceDataSerializer,
)


class ReceiveDeviceMetricsViewSet(viewsets.ModelViewSet):
    queryset = DeviceMetrics.objects.all()
    serializer_class = DeviceMetricsSerializer


class ListDeviceMetrics(ListAPIView):
    queryset = DeviceMetrics.objects.all()
    serializer_class = DeviceMetricsSerializer

    def get_queryset(self):
        return self.queryset.filter(device__id=self.kwargs["pk"])


class EnvironmentalParameterViewSet(viewsets.ModelViewSet):
    queryset = EnvironmentalParameter.objects.all().order_by("-created_at")
    serializer_class = EnvironmentalParameterSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, description="Export all items"),
            OpenApiParameter(name="count", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Number of items to export"),
            OpenApiParameter(name="page", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Page number to export"),
            OpenApiParameter(name="start_page", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Start page for range export"),
            OpenApiParameter(name="end_page", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="End page for range export"),
            OpenApiParameter(name="page_size", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="Page size (default 25)"),
        ],
        responses={200: {'content': {'text/csv': {}}}, 'description': 'CSV file download'},
        description="Export environmental parameters to CSV with flexible filtering options."
    )
    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        # Query params
        export_all = request.query_params.get("all", "false").lower() == "true"
        count = request.query_params.get("count")
        page = request.query_params.get("page")
        start_page = request.query_params.get("start_page")
        end_page = request.query_params.get("end_page")
        page_size = int(request.query_params.get("page_size", 25))

        queryset = self.get_queryset()

        # Pagination logic
        if export_all:
            data = queryset
        elif count:
            data = queryset[:int(count)]
        elif page:
            page = int(page)
            start = (page - 1) * page_size
            end = start + page_size
            data = queryset[start:end]
        elif start_page and end_page:
            start_page = int(start_page)
            end_page = int(end_page)
            start = (start_page - 1) * page_size
            end = end_page * page_size
            data = queryset[start:end]
        else:
            # Default: first page
            data = queryset[:page_size]

        # Prepare CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="environmental_parameters.csv"'
        writer = csv.writer(response)
        # Write header
        writer.writerow([
            "id", "device", "temperature", "pressure", "humidity", "air_quality", "ram_value", "system_temperature", "power_usage", "created_at"
        ])
        # Write data
        for obj in data:
            writer.writerow([
                obj.id,
                getattr(obj.device, 'device_id', obj.device),
                obj.temperature,
                obj.pressure,
                obj.humidity,
                obj.air_quality,
                obj.ram_value,
                obj.system_temperature,
                obj.power_usage,
                obj.created_at,
            ])
        return response


class SoundInferenceDataViewSet(viewsets.ModelViewSet):
    queryset = SoundInferenceData.objects.all().order_by("-created_at")
    serializer_class = SoundInferenceDataSerializer
