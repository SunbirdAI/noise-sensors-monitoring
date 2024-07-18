from django.contrib import admin

from .models import DeviceMetrics, EnvironmentalParameter, SoundInferenceData

admin.site.register(DeviceMetrics)


@admin.register(EnvironmentalParameter)
class EnvironmentalParameterAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "temperature",
        "pressure",
        "humidity",
        "air_quality",
        "ram_value",
        "system_temperature",
        "power_usage",
    )
    search_fields = ("device__device_id",)


@admin.register(SoundInferenceData)
class SoundInferenceDataAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "inference_probability",
        "inference_class",
        "inferred_audio_name",
    )
    search_fields = ("device__device_id", "inference_class")
