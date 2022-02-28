import logging
import pytz
from datetime import datetime, timedelta

from django.db.models import Avg, Max, Sum

from .models import DailyAnalysis
from devices.models import Device
from device_metrics.models import DeviceMetrics


logging.basicConfig(filename="app.log", 
    format="%(asctime)s - %(message)s",
    level=logging.INFO
)


def aggregate_daily_metrics():
    timezone = pytz.timezone("Africa/Kampala")
    yesterday = datetime.today() - timedelta(days=1)
    yesterday = timezone.localize(yesterday)
    devices = Device.objects.all()

    for device in devices:
        device_metrics = DeviceMetrics.objects.filter(
            device=device.id,
            time_uploaded__gt=yesterday
        )

        daily_avg_db_level = device_metrics.aggregate(Avg('avg_db_level'))
        daily_max_db_level = device_metrics.aggregate(Max('max_db_level'))
        daily_no_of_exceedances = device_metrics.aggregate(Sum('no_of_exceedances'))

        DailyAnalysis.objects.create(
            daily_avg_db_level=daily_avg_db_level,
            daily_max_db_level=daily_max_db_level,
            daily_no_of_exceedances=daily_no_of_exceedances,
            device=device
        )

        logging.info(f'Device metrics for device {device} aggregated')
