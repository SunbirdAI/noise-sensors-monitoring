from rest_framework import serializers

from analysis.serializers import DailyAnalysisSerializer, HourlyAnalysisSerializer
from recordings.models import Recording

from .models import Device, Location


class DeviceSerializer(serializers.ModelSerializer):
    lastseen = serializers.SerializerMethodField()
    get_metrics = serializers.SerializerMethodField()
    uptime = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = "__all__"

    def get_lastseen(self, obj):
        return getattr(obj, "lastseen", None)

    def get_get_metrics(self, obj):
        metrics = getattr(obj, "get_metrics", None)
        if metrics is None:
            return None

        try:
            from device_metrics.serializers import DeviceMetricsSerializer
        except ImportError:
            return str(metrics)  # fallback

        if hasattr(metrics, "all") or hasattr(metrics, "__iter__"):
            return DeviceMetricsSerializer(metrics, many=True).data

        if hasattr(metrics, "_meta"):
            return DeviceMetricsSerializer(metrics).data

        return metrics

    def get_uptime(self, obj):
        return getattr(obj, "uptime", None)


class DeviceLocationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="device_id")
    # latest_metric = HourlyAnalysisSerializer(read_only=True)

    class Meta:
        model = Location
        fields = [
            "id",
            "latitude",
            "longitude",
            "city",
            "division",
            "parish",
            "village",
            "location_description",
            "day_limit",
            "night_limit",
            "device_name",
        ]


class LocationMetricsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="device_id")
    location_hourly_metrics = HourlyAnalysisSerializer(read_only=True, many=True)
    location_daily_metrics = DailyAnalysisSerializer(read_only=True, many=True)

    class Meta:
        model = Location
        fields = [
            "id",
            "device_name",
            "location_hourly_metrics",
            "location_daily_metrics",
        ]


class RecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording
        fields = [
            "id",
            "time_recorded",
            "device",
            "category",
            "audio",
            "triggering_threshold",
        ]
        read_only_fields = ["time_uploaded"]


class LocationRecordingsSerializer(serializers.ModelSerializer):
    location_recordings = RecordingSerializer(read_only=True, many=True)

    class Meta:
        model = Location
        fields = ["id", "location_recordings"]


class DeviceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["configured", "device_id", "dbLevel", "recLength", "uploadAddr"]
