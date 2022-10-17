import uuid
from django.db import models
from django.utils import timezone

from devices.models import Device


class DailyAnalysis(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    date_analyzed = models.DateTimeField(default=timezone.now)
    daily_avg_db_level = models.FloatField(null=True)
    daily_median_db_level = models.FloatField(null=True)
    daily_max_db_level = models.FloatField(null=True)
    daily_no_of_exceedances = models.PositiveIntegerField(null=True)
    device = models.OneToOneField(Device, on_delete=models.CASCADE)


class HourlyAnalysis(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    date_analyzed = models.DateTimeField(default=timezone.now)
    hour_analyzed = models.PositiveIntegerField(null=True)
    hourly_avg_db_level = models.FloatField(null=True)
    hourly_median_db_level = models.FloatField(null=True)
    hourly_max_db_level = models.FloatField(null=True)
    hourly_no_of_exceedances = models.PositiveIntegerField(null=True)
    device = models.OneToOneField(Device, on_delete=models.CASCADE)
