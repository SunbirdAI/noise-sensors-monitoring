from rest_framework import serializers

from .models import HourlyAggregate, DailyAggregate


class HourlyAggregateSerializer(serializers.ModelSerializer):

    class Meta:
        model = HourlyAggregate
        fields = "__all__"


class DailyAggregateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyAggregate
        fields = "__all__"
