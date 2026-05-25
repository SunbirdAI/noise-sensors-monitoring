from datetime import datetime, timedelta, timezone as datetime_timezone

from django.core.paginator import Paginator
from django.db.models import Count, OuterRef, Q, Subquery
from django.utils import timezone

from analysis.models import MetricsTextFile
from device_metrics.models import DeviceMetrics, EnvironmentalParameter
from devices.models import Device
from recordings.models import Recording


ACTIVE_WINDOW = timedelta(hours=24)
HIGH_SYSTEM_TEMPERATURE = 75
STATUS_OPTIONS = (
    ("active", "Active"),
    ("inactive", "Inactive"),
    ("decommissioned", "Decommissioned"),
    ("issue", "Issue detected"),
)
DEVICE_TYPE_OPTIONS = (("MCU", "MCU"), ("MPU", "MPU"))
SORT_OPTIONS = (
    ("latest_reading", "Latest reading"),
    ("db_level", "dB level"),
    ("power_usage", "Power usage"),
    ("system_temperature", "System temperature"),
)
MIN_DATETIME = datetime.min.replace(tzinfo=datetime_timezone.utc)


def get_dashboard_queryset():
    latest_environmental = EnvironmentalParameter.objects.filter(
        device=OuterRef("pk")
    ).order_by("-created_at")
    latest_metrics = DeviceMetrics.objects.filter(device=OuterRef("pk")).order_by(
        "-time_uploaded"
    )
    latest_recording = Recording.objects.filter(device=OuterRef("pk")).order_by(
        "-time_uploaded"
    )
    latest_metrics_file = MetricsTextFile.objects.filter(device=OuterRef("pk")).order_by(
        "-time_uploaded"
    )

    return (
        Device.objects.select_related("location")
        .annotate(
            latest_environmental_id=Subquery(latest_environmental.values("id")[:1]),
            latest_environmental_time=Subquery(
                latest_environmental.values("created_at")[:1]
            ),
            latest_metrics_id=Subquery(latest_metrics.values("id")[:1]),
            latest_metrics_time=Subquery(latest_metrics.values("time_uploaded")[:1]),
            latest_recording_time=Subquery(latest_recording.values("time_uploaded")[:1]),
            latest_metrics_file_time=Subquery(
                latest_metrics_file.values("time_uploaded")[:1]
            ),
            samples_count=Count("recording", distinct=True),
        )
        .order_by("device_id")
    )


def apply_dashboard_search(queryset, search_term):
    if not search_term:
        return queryset

    return queryset.filter(
        Q(device_id__icontains=search_term)
        | Q(device_name__icontains=search_term)
        | Q(imei__icontains=search_term)
        | Q(location__city__icontains=search_term)
        | Q(location__division__icontains=search_term)
        | Q(location__parish__icontains=search_term)
        | Q(location__village__icontains=search_term)
    )


def build_device_health_rows(queryset):
    devices = list(queryset)
    environmental_records = EnvironmentalParameter.objects.in_bulk(
        [
            device.latest_environmental_id
            for device in devices
            if device.latest_environmental_id is not None
        ]
    )
    metric_records = DeviceMetrics.objects.in_bulk(
        [device.latest_metrics_id for device in devices if device.latest_metrics_id]
    )

    return [
        build_device_health_row(
            device,
            environmental_records.get(device.latest_environmental_id),
            metric_records.get(device.latest_metrics_id),
        )
        for device in devices
    ]


def build_device_health_row(device, environmental_record=None, metric_record=None):
    last_reported = latest_datetime(
        device.latest_environmental_time,
        device.latest_metrics_time,
        device.latest_recording_time,
        device.latest_metrics_file_time,
    )
    device_type_value, device_type_label = resolve_device_type(
        device, environmental_record, metric_record
    )
    status_value, status_label = resolve_status(
        device, last_reported, environmental_record
    )
    location = getattr(device, "location", None)

    return {
        "device": device,
        "device_id": device.device_id,
        "device_name": device.device_name,
        "imei": device.imei,
        "device_type": device_type_label,
        "device_type_value": device_type_value,
        "status": status_value,
        "status_label": status_label,
        "last_reported": last_reported,
        "location": format_location(location),
        "production_stage": device.production_stage,
        "samples_count": device.samples_count,
        "battery_level": value_or_none(getattr(metric_record, "battery_voltage", None)),
        "signal_strength": value_or_none(getattr(metric_record, "sig_strength", None)),
        "data_balance": value_or_none(getattr(metric_record, "data_balance", None)),
        "network_status": resolve_network_status(metric_record),
        "temperature": value_or_none(getattr(environmental_record, "temperature", None)),
        "pressure": value_or_none(getattr(environmental_record, "pressure", None)),
        "humidity": value_or_none(getattr(environmental_record, "humidity", None)),
        "air_quality": value_or_none(getattr(environmental_record, "air_quality", None)),
        "ram_value": value_or_none(getattr(environmental_record, "ram_value", None)),
        "system_temperature": value_or_none(
            getattr(environmental_record, "system_temperature", None)
        ),
        "power_usage": value_or_none(getattr(environmental_record, "power_usage", None)),
        "db_level": value_or_none(
            getattr(environmental_record, "db_level", None)
            if environmental_record
            else getattr(metric_record, "db_level", None)
        ),
    }


def latest_datetime(*values):
    dates = [value for value in values if value is not None]
    return max(dates, default=None)


def resolve_device_type(device, environmental_record=None, metric_record=None):
    if device.device_type:
        return device.device_type, device.get_device_type_display()
    if environmental_record:
        return Device.DeviceType.MPU, Device.DeviceType.MPU.label
    if metric_record:
        return Device.DeviceType.MCU, Device.DeviceType.MCU.label
    return "", "N/A"


def resolve_status(device, last_reported=None, environmental_record=None):
    if device.production_stage == Device.ProductionStage.RETIRED:
        return "decommissioned", "Decommissioned"
    if device.production_stage == Device.ProductionStage.MAINTENANCE:
        return "issue", "Issue detected"
    if (
        environmental_record
        and environmental_record.system_temperature is not None
        and environmental_record.system_temperature >= HIGH_SYSTEM_TEMPERATURE
    ):
        return "issue", "Issue detected"
    if device.production_stage != Device.ProductionStage.DEPLOYED:
        return "inactive", "Inactive"
    if last_reported and last_reported >= timezone.now() - ACTIVE_WINDOW:
        return "active", "Active"
    return "issue", "Issue detected"


def resolve_network_status(metric_record=None):
    if metric_record is None or metric_record.sig_strength is None:
        return "N/A"
    if metric_record.sig_strength >= 20:
        return "Good"
    if metric_record.sig_strength >= 10:
        return "Fair"
    return "Poor"


def format_location(location):
    if not location:
        return "N/A"
    parts = [
        location.village,
        location.parish,
        location.division,
        location.city,
    ]
    cleaned = [part for part in parts if part and part != "N/A"]
    return ", ".join(cleaned) if cleaned else "N/A"


def value_or_none(value):
    return None if value in ("", None) else value


def filter_rows(rows, status=None, device_type=None):
    if status:
        rows = [row for row in rows if row["status"] == status]
    if device_type:
        rows = [row for row in rows if row["device_type_value"] == device_type]
    return rows


def sort_rows(rows, sort_by=None):
    if sort_by == "db_level":
        return sorted(
            rows, key=lambda row: number_sort_value(row["db_level"]), reverse=True
        )
    if sort_by == "power_usage":
        return sorted(
            rows, key=lambda row: number_sort_value(row["power_usage"]), reverse=True
        )
    if sort_by == "system_temperature":
        return sorted(
            rows,
            key=lambda row: number_sort_value(row["system_temperature"]),
            reverse=True,
        )
    return sorted(
        rows,
        key=lambda row: row["last_reported"] or MIN_DATETIME,
        reverse=True,
    )


def number_sort_value(value):
    return float(value) if value is not None else float("-inf")


def build_dashboard_summary(rows):
    return {
        "total_sensors": len(rows),
        "active_sensors": sum(1 for row in rows if row["status"] == "active"),
        "inactive_sensors": sum(1 for row in rows if row["status"] == "inactive"),
        "decommissioned_sensors": sum(
            1 for row in rows if row["status"] == "decommissioned"
        ),
        "issue_sensors": sum(1 for row in rows if row["status"] == "issue"),
        "deployed_sensors": sum(
            1
            for row in rows
            if row["production_stage"] == Device.ProductionStage.DEPLOYED
        ),
        "total_samples": Recording.objects.count(),
        "samples_today": Recording.objects.filter(
            time_recorded__date=timezone.localdate()
        ).count(),
    }


def paginate_rows(rows, page_number, page_size=20):
    paginator = Paginator(rows, page_size)
    return paginator.get_page(page_number)
