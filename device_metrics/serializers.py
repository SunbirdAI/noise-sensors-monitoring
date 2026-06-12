from rest_framework import serializers

from devices.models import Device

from .models import DeviceMetrics, EnvironmentalParameter, SoundInferenceData


class DeviceMetricsSerializer(serializers.ModelSerializer):
    # device = serializers.PrimaryKeyRelatedField(queryset=Device.objects.all())
    device = serializers.SlugRelatedField(
        queryset=Device.objects.all(), slug_field="device_id"
    )

    class Meta:
        model = DeviceMetrics
        fields = [
            "id",
            "device",
            "sig_strength",
            "db_level",
            "avg_db_level",
            "max_db_level",
            "no_of_exceedances",
            "last_rec",
            "last_upl",
            "panel_voltage",
            "battery_voltage",
            "data_balance",
            "time_uploaded",
        ]
        read_only_fields = ["time_uploaded"]


class EnvironmentalParameterSerializer(serializers.ModelSerializer):
    device = serializers.SlugRelatedField(
        queryset=Device.objects.all(), slug_field="device_id"
    )

    class Meta:
        model = EnvironmentalParameter
        fields = [
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


class SoundInferenceDataSerializer(serializers.ModelSerializer):
    device = serializers.SlugRelatedField(
        queryset=Device.objects.all(), slug_field="device_id"
    )

    class Meta:
        model = SoundInferenceData
        fields = [
            "id",
            "device",
            "inference_probability",
            "inference_class",
            "inferred_audio_name",
            "created_at",
        ]


class HistoryRangeSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(allow_null=True)
    end_date = serializers.DateTimeField(allow_null=True)
    timezone = serializers.CharField()


class HistoryDeviceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    device_id = serializers.CharField()
    type = serializers.CharField(allow_blank=True)


class DeviceMetricsHistoryResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    range = HistoryRangeSerializer()
    device = HistoryDeviceSerializer()
    results = DeviceMetricsSerializer(many=True)


class EnvironmentalHistoryResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    range = HistoryRangeSerializer()
    device = HistoryDeviceSerializer()
    results = EnvironmentalParameterSerializer(many=True)


class SoundInferenceHistoryResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    range = HistoryRangeSerializer()
    device = HistoryDeviceSerializer()
    results = SoundInferenceDataSerializer(many=True)


class DeviceMetricAggregateSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    db_level = serializers.FloatField(required=False)
    avg_db_level = serializers.FloatField(allow_null=True)
    max_db_level = serializers.FloatField(allow_null=True)
    median_db_level = serializers.FloatField(allow_null=True)
    min_db_level = serializers.FloatField(allow_null=True)
    no_of_exceedances = serializers.IntegerField()
    reading_count = serializers.IntegerField()


class DeviceMetricAggregateResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    range = HistoryRangeSerializer()
    device = HistoryDeviceSerializer()
    results = DeviceMetricAggregateSerializer(many=True)
