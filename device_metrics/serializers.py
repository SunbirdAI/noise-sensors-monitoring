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
