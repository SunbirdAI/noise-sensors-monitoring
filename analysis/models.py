import uuid
from django.db import models

from devices.models import Device


class DailyAnalysis(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    daily_avg_db_level = models.FloatField()
    daily_max_db_level = models.FloatField()
    daily_no_of_exceedances = models.PositiveIntegerField()
    device = models.OneToOneField(Device, on_delete=models.CASCADE)
