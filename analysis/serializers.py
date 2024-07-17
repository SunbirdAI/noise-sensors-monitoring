from rest_framework import serializers

import devices.serializers
from devices.models import Device

from .models import DailyAggregate, HourlyAggregate, MetricsTextFile


class UploadMetricsTextFileSerializer(serializers.ModelSerializer):
    device = serializers.SlugRelatedField(
        queryset=Device.objects.all(), slug_field="device_id"
    )

    class Meta:
        model = MetricsTextFile
        fields = ["id", "metrics_file", "device"]
        read_only_fields = ["time_uploaded"]

    def to_representation(self, instance):
        self.fields["device"] = devices.serializers.DeviceSerializer(read_only=True)
        return {"result": "success"}


class ListMetricsTextFileSerializer(serializers.ModelSerializer):
    device = serializers.SlugRelatedField(
        queryset=Device.objects.all(), slug_field="device_id"
    )

    class Meta:
        model = MetricsTextFile
        fields = ["id", "time_uploaded", "device", "text_file_url"]


class HourlyAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourlyAggregate
        fields = "__all__"


class DailyAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAggregate
        fields = "__all__"
