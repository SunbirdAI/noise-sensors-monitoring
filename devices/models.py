import calendar
import uuid
from datetime import datetime, timedelta

import pytz
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase

from noise_dashboard.settings import TIME_ZONE


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Device(models.Model):
    class ProductionStage(models.TextChoices):
        DEPLOYED = "Deployed", _("Deployed")
        TESTING = "Testing", _("Testing")
        SHELVED = "Shelved", _("Shelved")
        MAINTENANCE = "Maintenance", _("Maintenance")
        RETIRED = "Retired", _("Retired")

    class Configured(models.IntegerChoices):
        CONFIGURED = (1, _("Configured"))
        NOT_CONFIGURED = (0, _("Not Configured"))

    class Mode(models.IntegerChoices):
        AUTO_MODE = (1, _("Auto"))
        MANUAL_MODE = (2, _("Manual"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=200, unique=True)
    imei = models.CharField(max_length=15)
    device_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=10)
    version_number = models.CharField(max_length=10)
    production_stage = models.CharField(
        max_length=50, choices=ProductionStage.choices, default=ProductionStage.TESTING
    )
    tags = TaggableManager(through=UUIDTaggedItem)
    metrics_url = models.URLField(max_length=255, default="http://localhost:3000/")

    # Configuration fields
    configured = models.IntegerField(
        choices=Configured.choices, default=Configured.NOT_CONFIGURED
    )
    mode = models.IntegerField(choices=Mode.choices, default=Mode.AUTO_MODE)
    dbLevel = models.IntegerField(default=50)
    recLength = models.IntegerField(default=10)
    recInterval = models.IntegerField(default=10)
    uploadAddr = models.CharField(
        default="http://localhost:8000/audio/", max_length=100
    )

    @property
    def lastseen(self):
        """
        Return the last seen time of the device. It prioritizes the following in order:
        1. Last metric text file uploaded time
        2. Last device metrics uploaded time
        3. Last recording uploaded time
        """
        # Fetch the last metric text file upload time
        last_metric_file = self.get_last_metric_text_file()

        # Fetch the last device metrics upload time
        last_device_metric = self.get_metrics.first()

        # Fetch the last recording uploaded time
        last_recording = self.get_recordings.first()

        # Compare and return the most recent time from all three sources
        timestamps = [
            last_metric_file.time_uploaded if last_metric_file else None,
            last_device_metric.time_uploaded if last_device_metric else None,
            last_recording.time_uploaded if last_recording else None
        ]

        # Filter out None values and return the latest timestamp
        valid_timestamps = [time for time in timestamps if time is not None]
        return max(valid_timestamps, default=None)

    def get_last_metric_text_file(self):
        try:
            # Retrieve the last metricstextfile uploaded for this device
            return self.metricstextfile_set.order_by("-time_uploaded").first()
        except self.metricstextfile_set.model.DoesNotExist:
            # Handle the case where there are no metricstextfiles
            return None

    def __str__(self):
        return self.device_id

    @property
    def get_recordings(self):
        return self.recording_set.order_by("-time_recorded")[:10]

    @property
    def get_metrics(self):
        return self.devicemetrics_set.order_by("-time_uploaded")[:10]

    @property
    def get_metric_files(self):
        return self.metricstextfile_set.order_by("-time_uploaded")[:20]

    def get_absolute_url(self):
        return reverse("device_detail", args=[str(self.id)])

    @property
    def uptime(self):
        """
        Calculate and return the uptime of the device.
        """
        return self.calculate_uptime(False)

    timezone = pytz.timezone(TIME_ZONE)

    def calculate_uptime(self, audio=True):
        """
        Returns gaps between upload times and total uptime. Returns a dictionary with:
        upload_gaps: Long gaps between uploads (1.5 hours or more)
        uptime: Number of hours/days since there was a 24-hour upload gap.
        """

        big_gaps = []
        went_online = None
        previous_downtime = None

        now = datetime.now(self.timezone)
        delta = timedelta(weeks=4)
        start_time = now - delta
        uploaded_times = self.get_uploaded_times(audio, now, start_time)
        uptime_percentages = self.calculate_monthly_uptime(uploaded_times)
        months = self.get_next_12_months()

        if not uploaded_times:
            return {
                "upload_gaps": [],
                "upload_gaps_len": 0,
                "uptime": 0,
                "previous_downtime": None,
                "uptime_percentages": [],
            }

        for date_from, date_to in zip(uploaded_times[:-1], uploaded_times[1:]):
            gap_time = date_to - date_from
            gap = round(gap_time.total_seconds() / 3600, 2)

            formatted_date_from = date_from.strftime("%Y-%m-%d %H:%M")
            formatted_date_to = date_to.strftime("%Y-%m-%d %H:%M")

            if gap > 3.0:
                big_gaps.append(
                    (gap, f"From {formatted_date_from} to {formatted_date_to}")
                )

            if gap >= 24 and not went_online:
                went_online = date_to
                previous_downtime = f"From {formatted_date_from} to {formatted_date_to}"

        if not went_online:
            went_online = start_time

        def_time = now - went_online
        uptime = round(max(0, def_time.total_seconds() / 3600), 2)

        return {
            "upload_gaps": big_gaps,
            "upload_gaps_len": len(big_gaps),
            "uptime": uptime,
            "previous_downtime": previous_downtime,
            "uptime_percentages": zip(months, uptime_percentages),
        }

    def get_uploaded_times(self, audio, now, start_time):
        query_set = self.recording_set if audio else self.metricstextfile_set

        try:
            files_dates = (
                query_set.filter(time_uploaded__range=[start_time, now])
                .values_list("time_uploaded", flat=True)
                .order_by("time_uploaded")
            )
            return list(files_dates)
        except query_set.model.DoesNotExist:
            # Handle the case where there are no metricstextfiles
            return []

    def get_next_12_months(self):
        current_month = datetime.now().replace(
            day=1
        )  # Get the first day of the current month
        months = [current_month]

        for _ in range(11):
            current_month = current_month + timedelta(
                days=31
            )  # Add an arbitrary number of days to move to the next month
            current_month = current_month.replace(
                day=1
            )  # Set the day to 1 to get the first day of the month
            months.append(current_month)

        return months

    def calculate_monthly_uptime(self, uploaded_times):
        current_month = datetime.now().month
        uptime_per_month = [0] * 12

        for upload_time in uploaded_times:
            month = upload_time.month - 1  # Adjust to 0-indexed
            uptime_per_month[month] += 1

        total_months = len(uptime_per_month)
        current_month_index = (current_month - 1) % total_months

        # Calculate uptime percentages
        uptime_percentages = [
            (count / (days * 24)) * 100
            for count, days in zip(
                uptime_per_month,
                [calendar.monthrange(2024, i)[1] for i in range(1, 13)],
            )
        ]

        # Shift the list so that the current month is at the beginning
        uptime_percentages = (
            uptime_percentages[current_month_index:]
            + uptime_percentages[:current_month_index]
        )

        return uptime_percentages

    def filter_time_by_month_and_year(self, time_formats, month, year):
        # Create an empty list to store the filtered time formats
        filtered_time_formats = []
        # Loop through each time format in the list
        for time_format in time_formats:
            # Parse the time format into a datetime object using the isoformat method
            datetime_object = datetime.datetime.fromisoformat(time_format)
            # Check if the month and year attributes of the datetime object match the given month and year
            if datetime_object.month == month and datetime_object.year == year:
                # If yes, append the time format to the filtered list
                filtered_time_formats.append(time_format)
        # Return the filtered list
        return filtered_time_formats

    def calculate_uptime_percentage(self, duration_weeks=4):
        """
        Calculate and return the uptime percentage of the device for a given duration.
        """
        now = datetime.now(self.timezone)
        delta = timedelta(weeks=duration_weeks)
        start_time = now - delta
        uptime_data = self.calculate_uptime(False)

        total_hours_in_duration = duration_weeks * 7 * 24
        return round((uptime_data["uptime"] / total_hours_in_duration) * 100, 2)


location_category_information = {
    "A": {
        "description": "Category A: hospital, convalescence home, sanatorium, home for the aged and "
        "higher learning institute, conference rooms, public library, "
        "environmental or recreational sites",
        "day_limit": 45,
        "night_limit": 35,
    },
    "B": {
        "description": "Category B: Residential buildings",
        "day_limit": 50,
        "night_limit": 35,
    },
    "C": {
        "description": "Category C: Mixed residential (with some commercial and entertainment)",
        "day_limit": 55,
        "night_limit": 45,
    },
    "D": {
        "description": "Category D: Residential + industry or small-scale production + commerce",
        "day_limit": 60,
        "night_limit": 50,
    },
    "E": {"description": "Category E: Industrial", "day_limit": 70, "night_limit": 60},
}


class Location(models.Model):
    class Category(models.TextChoices):
        A = "A", _(f'{location_category_information["A"]["description"]}')
        B = "B", _(f'{location_category_information["B"]["description"]}')
        C = "C", _(f'{location_category_information["C"]["description"]}')
        D = "D", _(f'{location_category_information["D"]["description"]}')
        E = "E", _(f'{location_category_information["E"]["description"]}')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=200)
    division = models.CharField(max_length=200, blank=True, default="N/A")
    parish = models.CharField(max_length=200, blank=True, default="N/A")
    village = models.CharField(max_length=200, blank=True, default="N/A")
    device = models.OneToOneField(Device, on_delete=models.CASCADE, null=True)
    category = models.CharField(
        max_length=50, choices=Category.choices, default=Category.E
    )

    @property
    def device_name(self):
        return self.device.device_id

    @property
    def location_description(self):
        return location_category_information[self.category]["description"]

    @property
    def night_limit(self):
        return location_category_information[self.category]["night_limit"]

    @property
    def day_limit(self):
        return location_category_information[self.category]["day_limit"]

    @property
    def latest_audio(self):
        return self.device.location_recordings.order_by("-date")[0]

    # @property
    # def latest_metric(self):
    #     return self.device.hourlyaggregate_set.order_by("-date")[0]

    @property
    def location_hourly_metrics(self):
        return self.device.hourlyaggregate_set.filter(
            date__range=[datetime.today() - timedelta(days=2), datetime.today()]
        ).order_by("-date")

    @property
    def location_daily_metrics(self):
        return self.device.dailyaggregate_set.filter(
            date__range=[datetime.today() - timedelta(weeks=4), datetime.today()]
        ).order_by("-date")

    @property
    def location_recordings(self):
        return self.device.recording_set.order_by("-time_uploaded")
