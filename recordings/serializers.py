from rest_framework import serializers

from devices.models import Device
from devices.serializers import DeviceSerializer

from .models import Recording


class UploadRecordingSerializer(serializers.ModelSerializer):
    device = serializers.SlugRelatedField(
        queryset=Device.objects.all(), slug_field="device_id"
    )

    class Meta:
        model = Recording
        fields = [
            "id",
            "time_recorded",
            "audio",
            "category",
            "device",
            "triggering_threshold",
        ]
        read_only_fields = ["time_uploaded"]

    def to_representation(self, instance):
        self.fields["device"] = DeviceSerializer(read_only=True)
        return {"result": "success"}
