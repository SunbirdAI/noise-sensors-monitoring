from rest_framework import serializers

from .models import HourlyAggregate, DailyAggregate


class HourlyAggregateSerializer(serializers.ModelSerializer):

    class Meta:
        model = HourlyAggregate
        fields = ['device_id']


class DailyAggregateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyAggregate
        fields = ['device_id']
