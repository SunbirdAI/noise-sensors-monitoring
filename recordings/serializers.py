from rest_framework import serializers
from .models import Recording
from devices.models import Device
from devices.serializers import DeviceSerializer


class RecordingSerializer(serializers.ModelSerializer):
    device = serializers.SlugRelatedField(queryset=Device.objects.all(),
                                          slug_field='device_id')

    class Meta:
        model = Recording
        fields = ['id', 'time_recorded', 'audio', 'device']
        read_only_fields = ['time_uploaded']

    def to_representation(self, instance):
        self.fields['device'] = DeviceSerializer(read_only=True)
        return super(RecordingSerializer, self).to_representation(instance)
