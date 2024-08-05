import uuid

from django.core.validators import MaxValueValidator
from django.db import models

from devices.models import Device


class DeviceMetrics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    sig_strength = models.PositiveSmallIntegerField(validators=[MaxValueValidator(31)])
    db_level = models.FloatField()
    avg_db_level = models.FloatField(null=True)
    max_db_level = models.FloatField(null=True)
    no_of_exceedances = models.PositiveIntegerField(null=True)
    last_rec = models.PositiveIntegerField()
    last_upl = models.PositiveIntegerField()
    panel_voltage = models.FloatField()
    battery_voltage = models.FloatField()
    data_balance = models.PositiveIntegerField()
    time_uploaded = models.DateTimeField(auto_now_add=True)


class EnvironmentalParameter(models.Model):
    device = models.ForeignKey(
        Device,
        related_name="environmental_parameters",
        related_query_name="environmental_param",
        on_delete=models.CASCADE,
        help_text="Device ID",
    )
    temperature = models.FloatField(help_text="Environmental temperature", default=0.0)
    pressure = models.FloatField(help_text="Atmospheric pressure", default=0.0)
    humidity = models.FloatField(help_text="Atmospheric humidity", default=0.0)
    air_quality = models.FloatField(
        help_text="Volatile organic compounds vary resistance", default=0.0
    )
    ram_value = models.FloatField(help_text="Memory usage of the PI", default=0.0)
    system_temperature = models.FloatField(
        help_text="Temperature of the PI", default=0.0
    )
    power_usage = models.FloatField(
        help_text="Power utilization of the PI", default=0.0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.device.device_id} - Temp: {self.temperature}, Pressure: {self.pressure}, Humidity: {self.humidity}"


class SoundInferenceData(models.Model):
    device = models.ForeignKey(
        Device,
        related_name="inferences",
        related_query_name="sound_data",
        on_delete=models.CASCADE,
        help_text="Device ID",
    )
    inference_probability = models.FloatField(
        help_text="Probability of predicted class", default=0.0
    )
    inference_class = models.CharField(
        max_length=255, help_text="Name of predicted class"
    )
    inferred_audio_name = models.CharField(
        max_length=255, help_text="Name of inferred sound file"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Sound Inference Data"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.device.device_id} - {self.inference_class}: {self.inference_probability}"
