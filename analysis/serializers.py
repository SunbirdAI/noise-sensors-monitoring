from rest_framework import serializers

from .models import HourlyAggregate, DailyAggregate


class HourlyAnalysisSerializer(serializers.ModelSerializer):

    class Meta:
        model = HourlyAggregate
        fields = "__all__"


class DailyAnalysisSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyAggregate
        fields = "__all__"
