from django.contrib import admin

from .models import Device


class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "device_id",
        "imei",
        "device_name",
        "phone_number",
        "production_stage",
    )


admin.site.register(Device, DeviceAdmin)
