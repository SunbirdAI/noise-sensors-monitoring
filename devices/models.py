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
    uploadAddr = models.CharField(default="http://localhost:8000/audio/", max_length=100)

    def __str__(self):
        return self.device_id

    @property
    def get_recordings(self):
        return self.recording_set.order_by("-time_recorded")[:10]

    @property
    def get_metrics(self):
        return self.devicemetrics_set.order_by("-time_uploaded")[:10]

    def get_absolute_url(self):
        return reverse("device_detail", args=[str(self.id)])


location_category_information = {
    'A': {
        'description': 'Category A: hospital, convalescence home, sanatorium, home for the aged and '
                       'higher learning institute, conference rooms, public library, '
                       'environmental or recreational sites',
        'day_limit': 45,
        'night_limit': 35
    },
    'B': {
        'description': 'Category B: Residential buildings',
        'day_limit': 50,
        'night_limit': 35
    },
    'C': {
        'description': 'Category C: Mixed residential (with some commercial and entertainment)',
        'day_limit': 55,
        'night_limit': 45
    },
    'D': {
        'description': 'Category D: Residential + industry or small-scale production + commerce',
        'day_limit': 60,
        'night_limit': 50
    },
    'E': {
        'description': 'Category E: Industrial',
        'day_limit': 70,
        'night_limit': 60
    }
}


class Location(models.Model):
    class Category(models.TextChoices):
        A = 'A', _(f'{location_category_information["A"]["description"]}')
        B = 'B', _(f'{location_category_information["B"]["description"]}')
        C = 'C', _(f'{location_category_information["C"]["description"]}')
        D = 'D', _(f'{location_category_information["D"]["description"]}')
        E = 'E', _(f'{location_category_information["E"]["description"]}')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=200)
    division = models.CharField(max_length=200, blank=True, default="N/A")
    parish = models.CharField(max_length=200, blank=True, default="N/A")
    village = models.CharField(max_length=200, blank=True, default="N/A")
    device = models.OneToOneField(Device, on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.E)

    @property
    def location_description(self):
        return location_category_information[self.category]['description']

    @property
    def night_limit(self):
        return location_category_information[self.category]['night_limit']

    @property
    def day_limit(self):
        return location_category_information[self.category]['day_limit']

    @property
    def latest_metric(self):
        return self.device.devicemetrics_set.order_by("-time_uploaded")[0]

    @property
    def location_metrics(self):
        return self.device.devicemetrics_set.order_by("-time_uploaded")
