from rest_framework import serializers
from .models import DeviceMetrics


class DeviceMetricsFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceMetrics


class DeviceMetricsPartialSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceMetrics
        fields = ['db_level', 'datetime_uploaded']