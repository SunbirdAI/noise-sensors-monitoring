from rest_framework import serializers
from .models import Recording


class RecordingSerializer(serializers.ModelSerializer):
    device = serializers.StringRelatedField()

    class Meta:
        model = Recording
        fields = ['id', 'recording_name', 'time_recorded', 'time_uploaded', 's3bucket_url', 'device']
