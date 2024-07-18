import logging
from datetime import datetime

import pytz
from django.db.models import Avg, Max, Sum

from device_metrics.models import DeviceMetrics
from devices.models import Device
from noise_dashboard.settings import TIME_ZONE

from .models import DailyAnalysis

logging.basicConfig(
    filename="app.log", format="%(asctime)s - %(message)s", level=logging.INFO
)


def aggregate_daily_metrics():
    timezone = pytz.timezone(TIME_ZONE)
    today = datetime.today()
    today = timezone.localize(today)
    devices = Device.objects.all()

    for device in devices:
        device_metrics = DeviceMetrics.objects.filter(
            device=device.id,
            time_uploaded__year=today.year,
            time_uploaded__month=today.month,
            time_uploaded__day=today.day,
        )

        daily_avg_db_level = device_metrics.aggregate(Avg("avg_db_level"))
        daily_max_db_level = device_metrics.aggregate(Max("max_db_level"))
        daily_no_of_exceedances = device_metrics.aggregate(Sum("no_of_exceedances"))

        DailyAnalysis.objects.create(
            date_analyzed=today,
            daily_avg_db_level=daily_avg_db_level["avg_db_level__avg"],
            daily_max_db_level=daily_max_db_level["max_db_level__max"],
            daily_no_of_exceedances=daily_no_of_exceedances["no_of_exceedances__sum"],
            device=device,
        )

        logging.info(f"Daily device metrics for device {device} aggregated")
