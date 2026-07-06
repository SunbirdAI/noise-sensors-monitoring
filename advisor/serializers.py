from rest_framework import serializers


class AdvisorRangeSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()


class AdvisorInsightResponseSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    lang = serializers.ChoiceField(choices=["en", "lug"])
    audience = serializers.ChoiceField(choices=["resident", "official"])
    insight = serializers.CharField(allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(
        choices=["ready", "generating", "empty", "unavailable"]
    )
    cached = serializers.BooleanField()
    generated_at = serializers.DateTimeField(allow_null=True)
    range = AdvisorRangeSerializer()
