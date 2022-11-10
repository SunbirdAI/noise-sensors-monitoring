from rest_framework import serializers

from .models import HourlyAggregate, DailyAggregate


class ReceiveIoTMetricsSerializer(serializers.ListSerializer):
    date = serializers.DateField()
    device_id = serializers.CharField(max_length=200)
    db_level = serializers.FloatField()
