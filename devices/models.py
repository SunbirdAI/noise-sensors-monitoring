import uuid
from django.utils.translation import gettext_lazy as _

from django.db import models


class Device(models.Model):
    class ProductionStage(models.TextChoices):
        DEPLOYED = 'DL', _('Deployed')
        TESTING = 'TS', _('Testing')
        RECALLED = 'RC', _('Recalled')
        FIXING = 'FX', _('Fixing')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    device_id = models.CharField(max_length=200)
    imei = models.CharField(max_length=15)
    device_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=10)
    production_stage = models.CharField(
        max_length=2,
        choices=ProductionStage.choices,
        default=ProductionStage.TESTING
    )

    def __str__(self):
        return self.device_id
