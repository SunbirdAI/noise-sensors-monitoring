from rest_framework import serializers
from .models import Recording
from devices.serializers import DeviceSerializer


class RecordingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recording
        fields = ['id', 'recording_name', 'time_recorded', 'audio', 'device']
        read_only_fields = ['time_uploaded']

    def to_representation(self, instance):
        self.fields['device'] = DeviceSerializer(read_only=True)
        return super(RecordingSerializer, self).to_representation(instance)
