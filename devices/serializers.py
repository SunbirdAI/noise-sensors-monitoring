from rest_framework import serializers
from .models import Device, Location


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ['device_id']


class LocationSerializer(serializers.ModelField):

    class Meta:
        model = Location
        fields = ['longitude', 'latitude', 'city', 'place_name']


class DeviceConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ['configured', 'device_id', 'dbLevel', 'recLength', 'uploadAddr']
