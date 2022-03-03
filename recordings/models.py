from django.utils import timezone
from django.core.files.storage import get_storage_class

from django.db import models

from devices.models import Device


media_storage = get_storage_class()()


def recording_directory(instance, filename):
    time_recorded = instance.time_recorded.strftime("%Y-%m-%dT%H:%M:%S")
    return f'audio/{instance.device.device_id}/{instance.device.device_id}-{time_recorded}-{filename}'


class Recording(models.Model):
    class NoiseCategory(models.TextChoices):
        CAR_OR_TRUCK = 'car-or-truck', _('car-or-truck')
        MOTOR_VEHICHLE_HORN = 'motor-vehicle-horn', _('motor-vehicle-horn')
        BODABODA_MOTORCYCLE = 'bodaboda-motorcycle', _('bodaboda-motorcycle')
        MOTOR_VEHICHLE_SIREN = 'motor-vehicle-siren', _('motor-vehicle-siren')
        CAR_ALARM = 'car-alarm', _('car-alarm')
        MOBILE_MUSIC = 'mobile-music', _('mobile-music')
        HAWKER_VENDOR = 'hawker-vendor', _('hawker-vendor')
        COMMUNITY_RADIO = 'community-radio', _('community-radio')
        RELIGIOUS_VENUE = 'religious-venue', _('religious-venue')
        HERBALIST = 'herbalist', _('herbalists')
        CONSTRUCTION_SITE = 'construction-site', _('construction-site')
        FABRICATION_WORKSHOP = 'fabrication-workshop', _('fabrication-workshop')
        GENERATOR = 'generator', _('generator')
        BAR_RESTAURANT_NIGHT_CLUB = 'bar/restaurant/night-club', _('bar/restaurant/night-club')
        ANIMAL = 'animal', _('animal')
        CROWD_NOISE = 'crowd-noise', _('crowd-noise')
        SCHOOL = 'school', _('school')
        STREET_PREACHER = 'street-preacher', _('street-preacher')
        OTHER = 'other', _('other')

    time_recorded = models.DateTimeField(default=timezone.now)
    time_uploaded = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    audio = models.FileField(upload_to=recording_directory)
    triggering_threshold = models.IntegerField(default=50)
    category = models.CharField(
        max_length=30,
        choices=NoiseCategory.choices,
        default=None,
        null=True
    )

    @property
    def audio_url(self):
        return media_storage.url(self.audio.name)
