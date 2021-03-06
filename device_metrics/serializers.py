from rest_framework import serializers
from .models import DeviceMetrics
from devices.models import Device


class DeviceMetricsSerializer(serializers.ModelSerializer):
    # device = serializers.PrimaryKeyRelatedField(queryset=Device.objects.all())
    device = serializers.SlugRelatedField(queryset=Device.objects.all(),
                                          slug_field='device_id')

    class Meta:
        model = DeviceMetrics
        fields = [
                'device', 'sig_strength', 'db_level', 'avg_db_level', 'max_db_level',
                'no_of_exceedances', 'last_rec', 'last_upl', 'panel_voltage',
                'battery_voltage', 'data_balance', 'time_uploaded'
            ]
        read_only_fields = ['time_uploaded']
