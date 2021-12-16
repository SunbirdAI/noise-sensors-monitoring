from django.forms import ModelForm
from .models import DeviceMetrics


class DeviceMetricsForm(ModelForm):
    class Meta:
        model = DeviceMetrics
        fields = [
                  'device', 'sig_strength', 'db_level', 'last_rec',
                  'last_upl', 'panel_voltage', 'battery_voltage',
                  'data_balance'
                 ]
