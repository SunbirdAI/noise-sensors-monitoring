import uuid

from django.db import models
from django.db.models.fields import PositiveIntegerField, PositiveSmallIntegerField
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
    db_level = models.PositiveIntegerField()
    last_rec = models.PositiveIntegerField()
    last_upl = models.PositiveIntegerField()
    panel_voltage = models.PositiveIntegerField()
    battery_voltage = models.PositiveIntegerField()
    data_balance = models.PositiveIntegerField()
    time_uploaded = models.DateTimeField(auto_now_add=True)
