from rest_framework import serializers

from device_metrics.serializers import DeviceMetricsSerializer
from recordings.models import Recording
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


class LocationMetricsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='device_id')
    location_metrics = DeviceMetricsSerializer(read_only=True, many=True)

    class Meta:
        model = Location
        fields = [
            'id', 'location_metrics'
        ]


class RecordingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recording
        fields = ['id', 'time_recorded', 'category', 'audio', 'triggering_threshold']
        read_only_fields = ['time_uploaded']


class LocationRecordingsSerializer(serializers.ModelSerializer):
    location_recordings = RecordingSerializer(read_only=True, many=True)

    class Meta:
        model = Location
        fields = [
            'id', 'location_recordings'
        ]


class DeviceConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ['configured', 'device_id',
                  'dbLevel', 'recLength', 'uploadAddr']
