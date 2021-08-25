from django.utils import timezone

from django.db import models

from devices.models import Device


class Recording(models.Model):
    recording_name = models.CharField(max_length=50)
    time_recorded = models.DateTimeField(default=timezone.now)
    time_uploaded = models.DateTimeField(auto_now_add=True)
    s3bucket_url = models.URLField(max_length=100)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
