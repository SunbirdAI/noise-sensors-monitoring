from django.db.models import Avg, FloatField, Max
from django.db.models.functions import Coalesce

from device_metrics.history import bucketed_metric_queryset, filter_by_date_range
from device_metrics.models import DeviceMetrics, SoundInferenceData
from devices.models import Location


def build_features(device, start, end, tz):
    location = _get_location(device)
    day_limit = location.day_limit if location else None
    night_limit = location.night_limit if location else None

    queryset = filter_by_date_range(
        DeviceMetrics.objects.filter(device=device),
        "time_uploaded",
        start,
        end,
    )
    readings = queryset.count()
    summary = queryset.aggregate(
        avg_db=Avg(Coalesce("avg_db_level", "db_level", output_field=FloatField())),
        peak_db=Max(Coalesce("max_db_level", "db_level", output_field=FloatField())),
    )

    avg_db = _round(summary["avg_db"])
    peak_db = _round(summary["peak_db"])

    return {
        "avg_db": avg_db,
        "peak_db": peak_db,
        "exceedances": _sum_exceedances(queryset),
        "day_limit": day_limit,
        "night_limit": night_limit,
        "pct_over_day": _percentage_over_limit(queryset, readings, day_limit),
        "pct_over_night": _percentage_over_limit(queryset, readings, night_limit),
        "loudest_hour": _loudest_bucket(queryset, "hourly", tz),
        "loudest_day": _loudest_bucket(queryset, "daily", tz),
        "dominant_sound": _dominant_sound(device),
        "readings": readings,
        "trend_vs_prev": _trend_vs_previous(device, start, end),
        "location_label": _location_label(location),
        "range": {
            "start_date": start.astimezone(tz).isoformat(),
            "end_date": end.astimezone(tz).isoformat(),
        },
    }


def _get_location(device):
    try:
        return device.location
    except (AttributeError, Location.DoesNotExist):
        return None


def _location_label(location):
    if location is None:
        return None

    parts = [
        value
        for value in [location.village, location.parish, location.city]
        if value and value != "N/A"
    ]
    return ", ".join(parts) if parts else None


def _sum_exceedances(queryset):
    total = 0
    for value in queryset.values_list("no_of_exceedances", flat=True):
        total += value or 0
    return total


def _percentage_over_limit(queryset, readings, limit):
    if limit is None or readings == 0:
        return None
    over_limit = queryset.filter(db_level__gt=limit).count()
    return _round((over_limit / readings) * 100)


def _loudest_bucket(queryset, granularity, tz):
    rows = list(bucketed_metric_queryset(queryset, granularity, "timestamp", tz))
    if not rows:
        return None

    row = max(
        rows,
        key=lambda candidate: candidate["max_db_level"]
        if candidate["max_db_level"] is not None
        else float("-inf"),
    )
    return {
        "timestamp": row["bucket"].astimezone(tz).isoformat(),
        "avg_db": _round(row["avg_db_level"]),
        "peak_db": _round(row["max_db_level"]),
        "readings": row["reading_count"],
    }


def _dominant_sound(device):
    return (
        SoundInferenceData.objects.filter(device=device)
        .order_by("-created_at")
        .values_list("inference_class", flat=True)
        .first()
    )


def _trend_vs_previous(device, start, end):
    duration = end - start
    previous_start = start - duration
    previous_end = start
    previous_queryset = filter_by_date_range(
        DeviceMetrics.objects.filter(device=device),
        "time_uploaded",
        previous_start,
        previous_end,
    )
    current_queryset = filter_by_date_range(
        DeviceMetrics.objects.filter(device=device),
        "time_uploaded",
        start,
        end,
    )
    current_avg = current_queryset.aggregate(
        value=Avg(Coalesce("avg_db_level", "db_level", output_field=FloatField()))
    )["value"]
    previous_avg = previous_queryset.aggregate(
        value=Avg(Coalesce("avg_db_level", "db_level", output_field=FloatField()))
    )["value"]

    if current_avg is None or previous_avg is None:
        return None
    return _round(current_avg - previous_avg)


def _round(value):
    if value is None:
        return None
    return round(float(value), 2)
