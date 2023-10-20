from .models import Device
from datetime import datetime, timedelta
import pytz
from noise_dashboard.settings import TIME_ZONE

timezone = pytz.timezone(TIME_ZONE)


def calculate_uptime(device_id, weeks_past, audio=True):
    """
    Returns gaps between upload times and total uptime. Returns a dictionary with:
    upload_gaps: Long gaps between uploads (1.5 hours or more)
    uptime: Number of hours/days since there was a 24-hour upload gap.
    """
    now = timezone.localize(datetime.now())
    delta = timedelta(weeks=weeks_past)
    start_time = now - delta
    uploaded_times = get_uploaded_times(device_id, audio, now, start_time)
    return get_gaps(uploaded_times, now, start_time)


def timedelta_to_hours(delta: timedelta):
    seconds = delta.total_seconds()
    hours = seconds / 3600
    return hours


def get_uploaded_times(device_id, audio, now, start_time):
    device = Device.objects.get(device_id=device_id)
    query_set = device.recording_set if audio else device.metricstextfile_set
    files_dates = (query_set.filter(time_uploaded__range=[start_time, now])
                   .values_list('time_uploaded', flat=True)
                   .order_by('-time_uploaded'))
    return list(files_dates)


def get_gaps(uploaded_times, now, start_time):
    if len(uploaded_times) == 0:
        return {
            'big_gaps': [],
            'uptime': 0,
            'previous_downtime': None
        }
    big_gaps = []
    went_online = None
    previous_downtime = None
    for i in range(1, len(uploaded_times)):
        date_to = uploaded_times[i - 1]
        date_from = uploaded_times[i]
        gap = timedelta_to_hours(date_to - date_from)
        if gap > 1.5:
            big_gaps.append((gap, f"From {date_from} to {date_to}"))
        if gap >= 24 and not went_online:
            went_online = date_to
            previous_downtime = f"From {date_from} to {date_to}"

    if not went_online:
        went_online = start_time

    if timedelta_to_hours(now - uploaded_times[0]) >= 24:
        uptime = 0
    else:
        uptime = timedelta_to_hours(now - went_online)
    return {
        'upload_gaps': big_gaps,
        'uptime': uptime,
        'previous_downtime': previous_downtime
    }
