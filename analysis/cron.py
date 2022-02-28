import logging
import pytz
from datetime import datetime

from .models import DailyAnalysis
from devices.models import Device
from device_metrics.models import DeviceMetrics


logging.basicConfig(filename="app.log", 
    format="%(asctime)s - %(message)s",
    level=logging.INFO
)


def aggregate_daily_metrics():
    timezone = pytz.timezone("Africa/Kampala")
    today = datetime.today()
    today = timezone.localize(today)
    devices = Device.objects.all()

    for device in devices:
        device_metrics = DeviceMetrics.objects.filter(
            device=device.id,
            time_uploaded__gt=today # change this
        )
        daily_avg_db_level = 0 # calculate it here
        daily_max_db_level = 0 # calculate it here
        daily_no_of_exceedances = 0 # calculate it here

        DailyAnalysis.objects.create(
            daily_avg_db_level=daily_avg_db_level,
            daily_max_db_level=daily_max_db_level,
            daily_no_of_exceedances=daily_no_of_exceedances,
            device=device
        )

        logging.info(f'Device metrics for device {device} aggregated')

