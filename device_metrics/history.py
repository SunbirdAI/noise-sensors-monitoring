from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.core.paginator import EmptyPage
from django.db.models import Avg, Count, FloatField, IntegerField, Max, Min, Sum, Value
from django.db.models.functions import Coalesce, TruncDay, TruncHour
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


MAX_PAGE_SIZE = 500
DEFAULT_PAGE_SIZE = 25
DEFAULT_TIMEZONE = getattr(settings, "TIME_ZONE", "Africa/Kampala")

HISTORY_QUERY_PARAMS = {"start_date", "end_date", "page", "page_size", "ordering"}
AGGREGATE_QUERY_PARAMS = {
    "start_date",
    "end_date",
    "granularity",
    "timezone",
    "page",
    "page_size",
    "ordering",
}


class HistoryPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = MAX_PAGE_SIZE

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view)
        except EmptyPage as exc:
            raise NotFound("Invalid page.") from exc


def validate_query_params(request, allowed_params):
    unsupported = sorted(set(request.query_params.keys()) - allowed_params)
    if unsupported:
        raise ValidationError(
            {"detail": "Unsupported query parameter(s): " + ", ".join(unsupported)}
        )

    page = request.query_params.get("page")
    if page is not None:
        validate_positive_int(page, "page")

    page_size = request.query_params.get("page_size")
    if page_size is not None:
        value = validate_positive_int(page_size, "page_size")
        if value > MAX_PAGE_SIZE:
            raise ValidationError(
                {
                    "page_size": f"page_size must be less than or equal to {MAX_PAGE_SIZE}."
                }
            )


def validate_positive_int(raw_value, field_name):
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field_name: "Must be a positive integer."}) from exc

    if value < 1:
        raise ValidationError({field_name: "Must be a positive integer."})

    return value


def get_timezone(timezone_name=None):
    try:
        return ZoneInfo(timezone_name or DEFAULT_TIMEZONE)
    except ZoneInfoNotFoundError as exc:
        raise ValidationError({"timezone": "Unknown timezone."}) from exc


def parse_date_range(request, tz=None):
    tz = tz or get_timezone()
    start_date = parse_optional_datetime(request.query_params.get("start_date"), tz)
    end_date = parse_optional_datetime(request.query_params.get("end_date"), tz)

    if start_date and end_date and start_date > end_date:
        raise ValidationError(
            {"detail": "start_date must be before or equal to end_date."}
        )

    return start_date, end_date


def parse_optional_datetime(raw_value, tz):
    if not raw_value:
        return None

    parsed = parse_datetime(raw_value)
    if parsed is None:
        raise ValidationError({"detail": f"Invalid datetime: {raw_value}"})

    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, tz)

    return parsed


def filter_by_date_range(queryset, timestamp_field, start_date, end_date):
    if start_date:
        queryset = queryset.filter(**{f"{timestamp_field}__gte": start_date})
    if end_date:
        queryset = queryset.filter(**{f"{timestamp_field}__lte": end_date})
    return queryset


def validate_ordering(request, allowed_fields, default_ordering):
    ordering = request.query_params.get("ordering", default_ordering)
    allowed = set(allowed_fields)
    allowed.update(f"-{field}" for field in allowed_fields)

    if ordering not in allowed:
        raise ValidationError(
            {
                "ordering": "Unsupported ordering. Supported values: "
                + ", ".join(sorted(allowed))
            }
        )

    return ordering


def device_summary(device):
    return {
        "id": str(device.id),
        "device_id": device.device_id,
        "type": device.device_type,
    }


def range_summary(start_date, end_date, tz):
    return {
        "start_date": format_datetime(start_date, tz),
        "end_date": format_datetime(end_date, tz),
        "timezone": getattr(tz, "key", str(tz)),
    }


def format_datetime(value, tz):
    if value is None:
        return None
    return value.astimezone(tz).isoformat()


def paginated_history_response(
    request,
    queryset,
    serializer_class,
    device,
    start_date,
    end_date,
    tz,
):
    paginator = HistoryPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(page, many=True)
    return Response(
        {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "range": range_summary(start_date, end_date, tz),
            "device": device_summary(device),
            "results": serializer.data,
        }
    )


def aggregate_payload(request, paginator, page, device, start_date, end_date, tz):
    return Response(
        {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "range": range_summary(start_date, end_date, tz),
            "device": device_summary(device),
            "results": page,
        }
    )


def paginated_raw_aggregate_response(
    request,
    queryset,
    device,
    start_date,
    end_date,
    tz,
):
    paginator = HistoryPagination()
    page = paginator.paginate_queryset(queryset, request)
    results = [raw_metric_row(metric, tz) for metric in page]
    return aggregate_payload(
        request, paginator, results, device, start_date, end_date, tz
    )


def paginated_bucketed_aggregate_response(
    request,
    queryset,
    granularity,
    ordering,
    device,
    start_date,
    end_date,
    tz,
):
    bucketed = bucketed_metric_queryset(queryset, granularity, ordering, tz)
    paginator = HistoryPagination()
    page = paginator.paginate_queryset(bucketed, request)
    results = [bucketed_metric_row(row, tz) for row in page]
    return aggregate_payload(
        request, paginator, results, device, start_date, end_date, tz
    )


def raw_metric_row(metric, tz):
    db_level = metric.db_level
    return {
        "timestamp": metric.time_uploaded.astimezone(tz).isoformat(),
        "db_level": db_level,
        "avg_db_level": metric.avg_db_level
        if metric.avg_db_level is not None
        else db_level,
        "max_db_level": metric.max_db_level
        if metric.max_db_level is not None
        else db_level,
        "median_db_level": db_level,
        "min_db_level": db_level,
        "no_of_exceedances": metric.no_of_exceedances or 0,
        "reading_count": 1,
    }


def bucketed_metric_queryset(queryset, granularity, ordering, tz):
    trunc_class = TruncHour if granularity == "hourly" else TruncDay
    order_by = "-bucket" if ordering == "-timestamp" else "bucket"
    return (
        queryset.annotate(bucket=trunc_class("time_uploaded", tzinfo=tz))
        .values("bucket")
        .annotate(
            avg_db_level=Avg(
                Coalesce("avg_db_level", "db_level", output_field=FloatField())
            ),
            max_db_level=Max(
                Coalesce("max_db_level", "db_level", output_field=FloatField())
            ),
            min_db_level=Min("db_level"),
            no_of_exceedances=Coalesce(
                Sum("no_of_exceedances"), Value(0), output_field=IntegerField()
            ),
            reading_count=Count("id"),
        )
        .order_by(order_by)
    )


def bucketed_metric_row(row, tz):
    return {
        "timestamp": row["bucket"].astimezone(tz).isoformat(),
        "avg_db_level": row["avg_db_level"],
        "max_db_level": row["max_db_level"],
        "median_db_level": None,
        "min_db_level": row["min_db_level"],
        "no_of_exceedances": row["no_of_exceedances"],
        "reading_count": row["reading_count"],
    }
