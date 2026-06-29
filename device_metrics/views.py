import csv

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from devices.models import Device

from .history import (
    AGGREGATE_QUERY_PARAMS,
    HISTORY_QUERY_PARAMS,
    filter_by_date_range,
    get_timezone,
    paginated_bucketed_aggregate_response,
    paginated_history_response,
    paginated_raw_aggregate_response,
    parse_date_range,
    validate_ordering,
    validate_query_params,
)
from .models import DeviceMetrics, EnvironmentalParameter, SoundInferenceData
from .serializers import (
    DeviceMetricAggregateResponseSerializer,
    DeviceMetricsHistoryResponseSerializer,
    DeviceMetricsSerializer,
    EnvironmentalHistoryResponseSerializer,
    EnvironmentalParameterSerializer,
    SoundInferenceHistoryResponseSerializer,
    SoundInferenceDataSerializer,
)


HISTORY_PARAMETERS = [
    OpenApiParameter(
        name="start_date",
        type=OpenApiTypes.DATETIME,
        location=OpenApiParameter.QUERY,
        description="Inclusive ISO 8601 datetime lower bound.",
    ),
    OpenApiParameter(
        name="end_date",
        type=OpenApiTypes.DATETIME,
        location=OpenApiParameter.QUERY,
        description="Inclusive ISO 8601 datetime upper bound.",
    ),
    OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Page number.",
    ),
    OpenApiParameter(
        name="page_size",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Items per page. Maximum 500.",
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="Sort order. Use newest first by default, or the timestamp field without '-' for oldest first.",
    ),
]

AGGREGATE_PARAMETERS = [
    OpenApiParameter(
        name="start_date",
        type=OpenApiTypes.DATETIME,
        location=OpenApiParameter.QUERY,
        description="Inclusive ISO 8601 datetime lower bound.",
    ),
    OpenApiParameter(
        name="end_date",
        type=OpenApiTypes.DATETIME,
        location=OpenApiParameter.QUERY,
        description="Inclusive ISO 8601 datetime upper bound.",
    ),
    OpenApiParameter(
        name="granularity",
        type=OpenApiTypes.STR,
        enum=["raw", "hourly", "daily"],
        location=OpenApiParameter.QUERY,
        description="Aggregation level. Defaults to raw.",
    ),
    OpenApiParameter(
        name="timezone",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="IANA timezone for buckets and returned range. Defaults to Africa/Kampala.",
    ),
    OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Page number.",
    ),
    OpenApiParameter(
        name="page_size",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Items per page. Maximum 500.",
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        enum=["timestamp", "-timestamp"],
        location=OpenApiParameter.QUERY,
        description="Bucket sort order. Defaults to timestamp.",
    ),
]

DEVICE_HISTORY_EXAMPLE = OpenApiExample(
    "SB device history",
    value={
        "count": 1234,
        "next": "https://noise-sensors-dashboard.herokuapp.com/device_metrics/device/by-device-id/SB1006/history/?page=2&page_size=100",
        "previous": None,
        "range": {
            "start_date": "2026-06-01T00:00:00+03:00",
            "end_date": "2026-06-12T23:59:59+03:00",
            "timezone": "Africa/Kampala",
        },
        "device": {
            "id": "1ec34468-e95d-46b3-89d8-5e186e5fef07",
            "device_id": "SB1006",
            "type": "MCU",
        },
        "results": [],
    },
    response_only=True,
)

SEAS_HISTORY_EXAMPLE = OpenApiExample(
    "SEAS environmental history",
    value={
        "count": 42,
        "next": None,
        "previous": None,
        "range": {
            "start_date": "2026-06-12T00:00:00+03:00",
            "end_date": "2026-06-12T23:59:59+03:00",
            "timezone": "Africa/Kampala",
        },
        "device": {
            "id": "d45c2f0f-b0da-46a5-bc9c-1ef22446d552",
            "device_id": "SEAS-2",
            "type": "MPU",
        },
        "results": [],
    },
    response_only=True,
)


class ReceiveDeviceMetricsViewSet(viewsets.ModelViewSet):
    queryset = DeviceMetrics.objects.all().order_by("-time_uploaded")
    serializer_class = DeviceMetricsSerializer


class ListDeviceMetrics(APIView):
    serializer_class = DeviceMetricsSerializer

    @extend_schema(
        parameters=HISTORY_PARAMETERS,
        responses={200: DeviceMetricsHistoryResponseSerializer},
        examples=[DEVICE_HISTORY_EXAMPLE],
        description=(
            "Return paginated device metric history for a device UUID. "
            "Supports inclusive start_date/end_date filtering and page_size up to 500. "
            "Default ordering is newest first (-time_uploaded)."
        ),
    )
    def get(self, request, pk):
        device = get_object_or_404(Device, pk=pk)
        queryset = DeviceMetrics.objects.filter(device=device)
        return device_metrics_history_response(request, device, queryset)


class LegacyListDeviceMetrics(ListDeviceMetrics):
    @extend_schema(exclude=True)
    def get(self, request, pk):
        return super().get(request, pk)


class DeviceMetricsByDeviceIdHistoryView(APIView):
    @extend_schema(
        parameters=HISTORY_PARAMETERS,
        responses={200: DeviceMetricsHistoryResponseSerializer},
        examples=[DEVICE_HISTORY_EXAMPLE],
        description=(
            "Return paginated device metric history for a public device_id, "
            "for example SB1006. This avoids a separate UUID lookup."
        ),
    )
    def get(self, request, device_id):
        device = get_object_or_404(Device, device_id=device_id)
        queryset = DeviceMetrics.objects.filter(device=device)
        return device_metrics_history_response(request, device, queryset)


class DeviceMetricsByDeviceIdAggregateView(APIView):
    @extend_schema(
        parameters=AGGREGATE_PARAMETERS,
        responses={200: DeviceMetricAggregateResponseSerializer},
        examples=[DEVICE_HISTORY_EXAMPLE],
        description=(
            "Return raw, hourly, or daily device metric buckets for charting. "
            "Timezone defaults to Africa/Kampala. Results are paginated with "
            "page_size up to 500."
        ),
    )
    def get(self, request, device_id):
        validate_query_params(request, AGGREGATE_QUERY_PARAMS)
        granularity = request.query_params.get("granularity", "raw")
        if granularity not in {"raw", "hourly", "daily"}:
            return Response(
                {"granularity": "Supported values are raw, hourly, and daily."},
                status=400,
            )

        ordering = request.query_params.get("ordering", "timestamp")
        if ordering not in {"timestamp", "-timestamp"}:
            return Response(
                {"ordering": "Supported values are timestamp and -timestamp."},
                status=400,
            )

        tz = get_timezone(request.query_params.get("timezone"))
        start_date, end_date = parse_date_range(request, tz)
        device = get_object_or_404(Device, device_id=device_id)
        queryset = filter_by_date_range(
            DeviceMetrics.objects.filter(device=device),
            "time_uploaded",
            start_date,
            end_date,
        )

        if granularity == "raw":
            raw_ordering = (
                "-time_uploaded" if ordering == "-timestamp" else "time_uploaded"
            )
            return paginated_raw_aggregate_response(
                request,
                queryset.order_by(raw_ordering),
                device,
                start_date,
                end_date,
                tz,
            )

        return paginated_bucketed_aggregate_response(
            request,
            queryset,
            granularity,
            ordering,
            device,
            start_date,
            end_date,
            tz,
        )


def device_metrics_history_response(request, device, queryset):
    validate_query_params(request, HISTORY_QUERY_PARAMS)
    tz = get_timezone()
    start_date, end_date = parse_date_range(request, tz)
    ordering = validate_ordering(request, ["time_uploaded"], "-time_uploaded")
    queryset = filter_by_date_range(
        queryset, "time_uploaded", start_date, end_date
    ).order_by(ordering)
    return paginated_history_response(
        request,
        queryset,
        DeviceMetricsSerializer,
        device,
        start_date,
        end_date,
        tz,
    )


def ai_history_response(
    request, device_id, model_class, serializer_class, timestamp_field
):
    validate_query_params(request, HISTORY_QUERY_PARAMS)
    device = get_object_or_404(Device, device_id=device_id)
    tz = get_timezone()
    start_date, end_date = parse_date_range(request, tz)
    ordering = validate_ordering(request, [timestamp_field], f"-{timestamp_field}")
    queryset = filter_by_date_range(
        model_class.objects.filter(device=device),
        timestamp_field,
        start_date,
        end_date,
    ).order_by(ordering)
    return paginated_history_response(
        request,
        queryset,
        serializer_class,
        device,
        start_date,
        end_date,
        tz,
    )


class EnvironmentalParameterViewSet(viewsets.ModelViewSet):
    queryset = EnvironmentalParameter.objects.all().order_by("-created_at")
    serializer_class = EnvironmentalParameterSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="all",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Export all items",
            ),
            OpenApiParameter(
                name="count",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of items to export",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number to export",
            ),
            OpenApiParameter(
                name="start_page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Start page for range export",
            ),
            OpenApiParameter(
                name="end_page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="End page for range export",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page size (default 25)",
            ),
            OpenApiParameter(
                name="year",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Year to filter records by (created_at year)",
            ),
        ],
        responses={200: OpenApiResponse(description="CSV file download.")},
        description="Export environmental parameters to CSV with flexible filtering options.",
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
        year = request.query_params.get("year")

        queryset = self.get_queryset()
        if year:
            queryset = queryset.filter(created_at__year=year)

        # Pagination logic
        if export_all:
            data = queryset
        elif count:
            data = queryset[: int(count)]
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
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="environmental_parameters.csv"'
        writer = csv.writer(response)
        # Write header
        writer.writerow(
            [
                "id",
                "device",
                "temperature",
                "pressure",
                "humidity",
                "air_quality",
                "ram_value",
                "system_temperature",
                "power_usage",
                "db_level",
                "created_at",
            ]
        )
        # Write data
        for obj in data:
            writer.writerow(
                [
                    obj.id,
                    getattr(obj.device, "device_id", obj.device),
                    obj.temperature,
                    obj.pressure,
                    obj.humidity,
                    obj.air_quality,
                    obj.ram_value,
                    obj.system_temperature,
                    obj.power_usage,
                    obj.db_level,
                    obj.created_at,
                ]
            )
        return response

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="device_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Device ID (string, not UUID)",
            ),
        ],
        responses={200: EnvironmentalParameterSerializer},
        description="Get the most recent environmental parameter for a device by device_id (string).",
    )
    @action(
        detail=False, methods=["get"], url_path="by-device-id/(?P<device_id>[^/.]+)"
    )
    def by_device_id(self, request, device_id=None):
        obj = (
            EnvironmentalParameter.objects.filter(device__device_id=device_id)
            .order_by("-created_at")
            .first()
        )
        if not obj:
            return Response({"detail": "Not found."}, status=404)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    @extend_schema(
        parameters=HISTORY_PARAMETERS,
        responses={200: EnvironmentalHistoryResponseSerializer},
        examples=[SEAS_HISTORY_EXAMPLE],
        description=(
            "Return paginated historical environmental readings for a SEAS device_id. "
            "The latest by-device-id endpoint remains unchanged."
        ),
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="by-device-id/(?P<device_id>[^/.]+)/history",
    )
    def by_device_id_history(self, request, device_id=None):
        return ai_history_response(
            request,
            device_id,
            EnvironmentalParameter,
            EnvironmentalParameterSerializer,
            "created_at",
        )


class SoundInferenceDataViewSet(viewsets.ModelViewSet):
    queryset = SoundInferenceData.objects.all().order_by("-created_at")
    serializer_class = SoundInferenceDataSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="device_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Device ID (string, not UUID)",
            ),
        ],
        responses={200: SoundInferenceDataSerializer},
        description="Get the most recent sound inference data for a device by device_id (string).",
    )
    @action(
        detail=False, methods=["get"], url_path="by-device-id/(?P<device_id>[^/.]+)"
    )
    def by_device_id(self, request, device_id=None):
        obj = (
            SoundInferenceData.objects.filter(device__device_id=device_id)
            .order_by("-created_at")
            .first()
        )
        if not obj:
            return Response({"detail": "Not found."}, status=404)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    @extend_schema(
        parameters=HISTORY_PARAMETERS,
        responses={200: SoundInferenceHistoryResponseSerializer},
        examples=[SEAS_HISTORY_EXAMPLE],
        description=(
            "Return paginated historical sound inference readings for a SEAS device_id. "
            "The latest by-device-id endpoint remains unchanged."
        ),
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="by-device-id/(?P<device_id>[^/.]+)/history",
    )
    def by_device_id_history(self, request, device_id=None):
        return ai_history_response(
            request,
            device_id,
            SoundInferenceData,
            SoundInferenceDataSerializer,
            "created_at",
        )
