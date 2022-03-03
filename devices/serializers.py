from rest_framework import serializers

from device_metrics.serializers import DeviceMetricsSerializer
from .models import Device, Location


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ['device_id']


class DeviceLocationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='device_id')
    latest_metric = DeviceMetricsSerializer(read_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'latitude', 'longitude', 'city',
            'division', 'parish', 'village', 'latest_metric'
        ]


class DeviceConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ['configured', 'device_id',
                  'dbLevel', 'recLength', 'uploadAddr']
