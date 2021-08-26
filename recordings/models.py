from django.utils import timezone

from django.db import models

from devices.models import Device


class Recording(models.Model):
    recording_name = models.CharField(max_length=50)
    time_recorded = models.DateTimeField(default=timezone.now)
    time_uploaded = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    audio = models.FileField(upload_to='audio/')
