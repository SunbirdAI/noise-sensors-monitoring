from django.utils import timezone

from django.db import models

from devices.models import Device


def recording_directory(instance, filename):
    return f'audio/{instance.device.device_id}/{filename}-{instance.time_uploaded}'


class Recording(models.Model):
    time_recorded = models.DateTimeField(default=timezone.now)
    time_uploaded = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    audio = models.FileField(upload_to=recording_directory)
    triggering_threshold = models.IntegerField(default=50)
