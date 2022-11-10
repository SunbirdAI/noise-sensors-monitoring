import pytz
from datetime import datetime

from noise_dashboard.settings import TIME_ZONE
from .models import DailyAggregate, HourlyAggregate
from devices.models import Device

timezone = pytz.timezone(TIME_ZONE)
today = datetime.today()
today = timezone.localize(today)
devices = Device.objects.all()


def aggregate_hourly(data):
    return "Hourly"


def aggregate_daily(data, type):

    return "Daily"
