from rest_framework import serializers

from analysis.serializers import HourlyAnalysisSerializer, DailyAnalysisSerializer
from recordings.models import Recording
from .models import Device, Location


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ['device_id']


class DeviceLocationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='device_id')
    # latest_metric = HourlyAnalysisSerializer(read_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'latitude', 'longitude', 'city',
            'division', 'parish', 'village', 'location_description', 'day_limit', 'night_limit',
        ]


class LocationMetricsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='device_id')
    location_hourly_metrics = HourlyAnalysisSerializer(read_only=True, many=True)
    location_daily_metrics = DailyAnalysisSerializer(read_only=True, many=True)
    class Meta:
        model = Location
        fields = [
            'id', 'device_name', 'location_hourly_metrics', 'location_daily_metrics'
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
