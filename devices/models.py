import uuid
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.urls import reverse

from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Device(models.Model):
    class ProductionStage(models.TextChoices):
        DEPLOYED = 'Deployed', _('Deployed')
        TESTING = 'Testing', _('Testing')
        SHELVED = 'Shelved', _('Shelved')
        MAINTENANCE = 'Maintenance', _('Maintenance')
        RETIRED = 'Retired', _('Retired')

    class Configured(models.IntegerChoices):
        CONFIGURED = (1, _("Configured"))
        NOT_CONFIGURED = (0, _("Not Configured"))

    class Mode(models.IntegerChoices):
        AUTO_MODE = (1, _("Auto"))
        MANUAL_MODE = (2, _("Manual"))

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    device_id = models.CharField(max_length=200, unique=True)
    imei = models.CharField(max_length=15)
    device_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=10)
    version_number = models.CharField(max_length=10)
    production_stage = models.CharField(
        max_length=50,
        choices=ProductionStage.choices,
        default=ProductionStage.TESTING
    )
    tags = TaggableManager(through=UUIDTaggedItem)
    metrics_url = models.URLField(max_length=255, default="http://localhost:3000/")

    # Configuration fields
    configured = models.IntegerField(choices=Configured.choices, default=Configured.NOT_CONFIGURED)
    mode = models.IntegerField(choices=Mode.choices, default=Mode.AUTO_MODE)
    dbLevel = models.IntegerField(default=50)
    recLength = models.IntegerField(default=10)
    recInterval = models.IntegerField(default=10)
    uploadAddr = models.CharField(default='http://localhost:8000/audio/', max_length=100)

    def __str__(self):
        return self.device_id

    def get_absolute_url(self):
        return reverse('device_detail', args=[str(self.id)])
