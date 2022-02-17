import uuid

from django.db import models
from django.core.validators import MaxValueValidator

from devices.models import Device

class DeviceMetrics(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    sig_strength = models.PositiveSmallIntegerField(
        validators = [MaxValueValidator(31)]
    )
    db_level = models.FloatField()
    avg_db_level = models.FloatField(null=True)
    max_db_level = models.FloatField(null=True)
    no_of_exceedances = models.PositiveIntegerField(null=True)
    last_rec = models.PositiveIntegerField()
    last_upl = models.PositiveIntegerField()
    panel_voltage = models.PositiveIntegerField()
    battery_voltage = models.PositiveIntegerField()
    data_balance = models.PositiveIntegerField()
    time_uploaded = models.DateTimeField(auto_now_add=True)
