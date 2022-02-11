from rest_framework import serializers
from .models import Device, Location


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ['device_id']


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = [
            'device', 'latitude', 'longitude', 'city', 
            'division', 'parish', 'village'
        ]


class DeviceConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ['configured', 'device_id', 'dbLevel', 'recLength', 'uploadAddr']
