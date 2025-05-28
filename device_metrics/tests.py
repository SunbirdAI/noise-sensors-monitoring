from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from devices.models import Device

from .models import EnvironmentalParameter, SoundInferenceData


class DeviceModelTest(TestCase):
    def setUp(self):
        self.device = Device.objects.create(device_id="device_001")

    def test_device_str(self):
        self.assertEqual(str(self.device), "device_001")


class EnvironmentalParameterModelTest(TestCase):
    def setUp(self):
        self.device = Device.objects.create(device_id="device_001")
        self.env_param = EnvironmentalParameter.objects.create(
            device=self.device,
            temperature=25.0,
            pressure=1013.25,
            humidity=45.0,
            air_quality=0.5,
            ram_value=512.0,
            system_temperature=50.0,
            power_usage=10.0,
        )

    def test_environmental_parameter_creation(self):
        self.assertIsInstance(self.env_param, EnvironmentalParameter)
        self.assertEqual(self.env_param.device.device_id, "device_001")
        self.assertEqual(self.env_param.temperature, 25.0)
        self.assertEqual(self.env_param.pressure, 1013.25)
        self.assertEqual(self.env_param.humidity, 45.0)
        self.assertEqual(self.env_param.air_quality, 0.5)
        self.assertEqual(self.env_param.ram_value, 512.0)
        self.assertEqual(self.env_param.system_temperature, 50.0)
        self.assertEqual(self.env_param.power_usage, 10.0)

    def test_environmental_parameter_str(self):
        expected_str = "device_001 - Temp: 25.0, Pressure: 1013.25, Humidity: 45.0"
        self.assertEqual(str(self.env_param), expected_str)


class SoundInferenceDataModelTest(TestCase):
    def setUp(self):
        self.device = Device.objects.create(device_id="device_001")
        self.sound_data = SoundInferenceData.objects.create(
            device=self.device,
            inference_probability=0.95,
            inference_class="Birdsong",
            inferred_audio_name="birdsong_001.wav",
        )

    def test_sound_inference_data_creation(self):
        self.assertIsInstance(self.sound_data, SoundInferenceData)
        self.assertEqual(self.sound_data.device.device_id, "device_001")
        self.assertEqual(self.sound_data.inference_probability, 0.95)
        self.assertEqual(self.sound_data.inference_class, "Birdsong")
        self.assertEqual(self.sound_data.inferred_audio_name, "birdsong_001.wav")

    def test_sound_inference_data_str(self):
        expected_str = "device_001 - Birdsong: 0.95"
        self.assertEqual(str(self.sound_data), expected_str)

    def test_verbose_name_plural(self):
        self.assertEqual(
            str(SoundInferenceData._meta.verbose_name_plural), "Sound Inference Data"
        )


class EnvironmentalParameterExportCsvTest(TestCase):
    def setUp(self):
        self.device = Device.objects.create(device_id="device_001")
        for i in range(30):
            EnvironmentalParameter.objects.create(
                device=self.device,
                temperature=20.0 + i,
                pressure=1000.0 + i,
                humidity=40.0 + i,
                air_quality=1.0 + i,
                ram_value=256.0 + i,
                system_temperature=45.0 + i,
                power_usage=5.0 + i,
            )
        self.client = APIClient()
        self.url = reverse("environmentalparameter-export-csv")

    def test_export_csv_default(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode()
        self.assertIn(
            "id,device,temperature,pressure,humidity,air_quality,ram_value,system_temperature,power_usage,created_at",
            content,
        )
        self.assertTrue(len(content.splitlines()) > 1)  # header + data

    def test_export_csv_all(self):
        response = self.client.get(self.url, {"all": "true"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # 30 rows + 1 header
        self.assertEqual(len(content.splitlines()), 31)

    def test_export_csv_count(self):
        response = self.client.get(self.url, {"count": 5})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertEqual(len(content.splitlines()), 6)  # 5 rows + 1 header

    def test_export_csv_page(self):
        response = self.client.get(self.url, {"page": 2, "page_size": 10})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertEqual(len(content.splitlines()), 11)  # 10 rows + 1 header

    def test_export_csv_page_range(self):
        response = self.client.get(
            self.url, {"start_page": 2, "end_page": 3, "page_size": 5}
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertEqual(len(content.splitlines()), 11)  # (pages 2 and 3 = 10 rows) + 1 header

    def test_export_csv_year(self):
        # Create records for a different year
        from datetime import datetime
        import pytz
        tz = pytz.UTC
        EnvironmentalParameter.objects.create(
            device=self.device,
            temperature=99.0,
            pressure=999.0,
            humidity=99.0,
            air_quality=9.0,
            ram_value=999.0,
            system_temperature=99.0,
            power_usage=9.0,
            created_at=tz.localize(datetime(2020, 5, 1, 12, 0, 0)),
        )
        # Get only current year records
        from datetime import datetime
        current_year = datetime.now().year
        response = self.client.get(self.url, {"year": current_year})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Should not include the 2020 record
        self.assertNotIn(
            "99.0,999.0,99.0,9.0,999.0,99.0,9.0", content
        )
        # Should include at least one of the current year records
        self.assertIn(str(current_year), content)

        # Get only 2020 records
        response = self.client.get(self.url, {"year": 2020})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("99.0,999.0,99.0,9.0,999.0,99.0,9.0", content)
