import uuid
from django.db import models
from django.utils import timezone
from django.core.files.storage import get_storage_class

from devices.models import Device


media_storage = get_storage_class()()


def recording_directory(instance, filename):
    time_uploaded = instance.time_uploaded.strftime("%Y-%m-%dT%H:%M:%S")
    return f'metrics/{instance.device.device_id}/{instance.device.device_id}-{time_uploaded}-{filename}'

class MetricsTextFile(models.Model):
    time_uploaded = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    metrics_file = models.FileField(upload_to=recording_directory)

    @property
    def text_file_url(self):
        return media_storage.url(self.metrics_file.name)

    @property
    def filename(self):
        return self.metrics_file.file.name


class HourlyAggregate(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    date = models.DateTimeField(default=timezone.now)
    hour = models.PositiveIntegerField(null=True)
    hourly_avg_db_level = models.FloatField(null=True)
    hourly_median_db_level = models.FloatField(null=True)
    hourly_max_db_level = models.FloatField(null=True)
    hourly_no_of_exceedances = models.PositiveIntegerField(null=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)


class DailyAggregate(models.Model):

    class TimePeriod(models.TextChoices):
        DAYTIME = 'daytime'
        NIGHTTIME = 'nighttime'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    date = models.DateTimeField(default=timezone.now)
    time_period = models.CharField(max_length=10, choices=TimePeriod.choices)
    daily_avg_db_level = models.FloatField(null=True)
    daily_median_db_level = models.FloatField(null=True)
    daily_max_db_level = models.FloatField(null=True)
    daily_no_of_exceedances = models.PositiveIntegerField(null=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
