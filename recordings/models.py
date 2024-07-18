import uuid

from django.core.files.storage import get_storage_class
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from devices.models import Device

media_storage = get_storage_class()()


def recording_directory(instance, filename):
    time_recorded = instance.time_recorded.strftime("%Y-%m-%dT%H:%M:%S")
    return f"audio/{instance.device.device_id}/{instance.device.device_id}-{time_recorded}-{filename}"


class Recording(models.Model):
    time_recorded = models.DateTimeField(default=timezone.now)
    time_uploaded = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    audio = models.FileField(upload_to=recording_directory)
    triggering_threshold = models.IntegerField(default=50)
    category = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(19)], null=True
    )

    @property
    def audio_url(self):
        return media_storage.url(self.audio.name)
