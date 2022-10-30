import pytz
from datetime import datetime

from noise_dashboard.settings import TIME_ZONE
from .models import DailyAggregate, HourlyAggregate
from devices.models import Device


def aggregate_results():
    timezone = pytz.timezone(TIME_ZONE)
    today = datetime.today()
    today = timezone.localize(today)
    devices = Device.objects.all()

    return [] # TO DO: calculate and return analysis result
