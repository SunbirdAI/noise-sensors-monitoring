import os

from dotenv import load_dotenv
import requests

load_dotenv()

BASE_URL = os.getenv('HTTP_APP_HOST')


class DevicesRepo:
    """
    Provides methods to access the devices stored in the Postgres DB via django methods
    """

    def __init__(self):
        pass

    def get_device_configuration_by_imei(self, imei_dict):
        imei = imei_dict["imei"]
        url = f"{BASE_URL}/devices/config/{imei}"
        response = requests.request("GET", url)
        if response.status_code == 200:
            return response.json()
        return {
            "error": response.status_code
        }
