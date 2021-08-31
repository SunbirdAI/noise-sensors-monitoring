import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'noise_dashboard.settings'
django.setup()

from devices.models import Device
from django.core.exceptions import ObjectDoesNotExist


class DevicesRepo:
    """
    Provides methods to access the devices stored in the Postgres DB via django methods
    """

    def __init__(self):
        pass

    def get_device_configuration_by_imei(self, imei_dict):
        try:
            device = Device.objects.get(imei=imei_dict["imei"])
            return {
                "configured": device.configured,
                "deviceId": device.device_id,
                "mode": device.mode,
                "recLength": device.recLength,
                "recInterval": device.recInterval,
                "uploadAddr": device.uploadAddr
            }
        except ObjectDoesNotExist:
            return {
                "error": f"No device with imei: {imei_dict['imei']}"
            }
