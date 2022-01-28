from rest_framework import serializers
from .models import DeviceMetrics
from devices.models import Device
from devices.serializers import DeviceSerializer


class DeviceMetricsFullSerializer(serializers.ModelSerializer):
    device = serializers.SlugRelatedField(queryset=Device.objects.all(),
                                          slug_field='device_id')

    class Meta:
        model = DeviceMetrics
        fields='__all__'

    def to_representation(self, instance):
        self.fields['device'] = DeviceSerializer(read_only=True)
        return {
            "result": "success"
        }


class DeviceMetricsPartialSerializer(serializers.ModelSerializer):
    device = serializers.SlugRelatedField(queryset=Device.objects.all(),
                                          slug_field='device_id')

    class Meta:
        model = DeviceMetrics
        fields = ['db_level', 'datetime_uploaded']
        read_only_fields = ['time_uploaded']

    def to_representation(self, instance):
        self.fields['device'] = DeviceSerializer(read_only=True)
        return {
            "result": "success"
        }