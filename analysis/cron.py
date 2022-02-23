from .models import DailyAnalysis
from devices.models import Device
from device_metrics.models import DeviceMetrics


def aggregate_daily_metrics():
    devices = Device.objects.all()
    for device in devices:
        daily_avg_db_level = 0 # calculate it here
        daily_max_db_level = 0 # calculate it here
        daily_no_of_exceedances = 0 # calculate it here

        DailyAnalysis.objects.create(
            daily_avg_db_level=daily_avg_db_level,
            daily_max_db_level=daily_max_db_level,
            daily_no_of_exceedances=daily_no_of_exceedances,
            device=device
        )
