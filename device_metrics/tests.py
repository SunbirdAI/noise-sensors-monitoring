from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from devices.models import Device

from .models import DeviceMetrics, EnvironmentalParameter, SoundInferenceData


def set_timestamp(instance, field_name, value):
    setattr(instance, field_name, value)
    instance.save(update_fields=[field_name])


def create_metric(
    device, uploaded_at, db_level=50.0, avg_db_level=None, max_db_level=None
):
    metric = DeviceMetrics.objects.create(
        device=device,
        sig_strength=31,
        db_level=db_level,
        avg_db_level=avg_db_level,
        max_db_level=max_db_level,
        no_of_exceedances=1,
        last_rec=0.0,
        last_upl=0.0,
        panel_voltage=18.0,
        battery_voltage=3.8,
        data_balance=300,
    )
    set_timestamp(metric, "time_uploaded", uploaded_at)
    return metric


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


class DeviceMetricsHistoryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.device = Device.objects.create(
            device_id="SB1006",
            imei="123456789012345",
            device_name="Naguru Summit View",
            phone_number="0700000000",
            version_number="1",
            production_stage="Deployed",
            device_type=Device.DeviceType.MCU,
        )
        self.other_device = Device.objects.create(
            device_id="SB9999",
            imei="123456789012346",
            device_name="Other sensor",
            phone_number="0700000001",
            version_number="1",
            production_stage="Deployed",
            device_type=Device.DeviceType.MCU,
        )
        self.start = timezone.make_aware(datetime(2026, 6, 1, 0, 0, 0))
        create_metric(self.device, self.start + timedelta(hours=1), 45.0, 44.0, 50.0)
        create_metric(self.device, self.start + timedelta(hours=2), 55.0, 54.0, 60.0)
        create_metric(self.device, self.start + timedelta(days=3), 65.0, 64.0, 70.0)
        create_metric(
            self.other_device, self.start + timedelta(hours=1), 99.0, 99.0, 99.0
        )

    def test_uuid_history_filters_by_date_and_pages_results(self):
        response = self.client.get(
            reverse("device_device_metrics", kwargs={"pk": self.device.id}),
            {
                "start_date": (self.start + timedelta(minutes=30)).isoformat(),
                "end_date": (self.start + timedelta(hours=2, minutes=30)).isoformat(),
                "page_size": 1,
                "ordering": "time_uploaded",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIsNotNone(response.data["next"])
        self.assertEqual(response.data["device"]["device_id"], "SB1006")
        self.assertEqual(response.data["device"]["type"], "MCU")
        self.assertEqual(response.data["results"][0]["db_level"], 45.0)
        self.assertEqual(response.data["range"]["timezone"], "Africa/Kampala")

    def test_by_device_id_history_avoids_uuid_lookup(self):
        response = self.client.get(
            reverse(
                "device_metrics_by_device_id_history",
                kwargs={"device_id": self.device.device_id},
            ),
            {"page_size": 2, "ordering": "time_uploaded"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["device"], "SB1006")

    def test_future_date_range_returns_empty_results(self):
        response = self.client.get(
            reverse(
                "device_metrics_by_device_id_history",
                kwargs={"device_id": self.device.device_id},
            ),
            {
                "start_date": "2099-01-01T00:00:00+03:00",
                "end_date": "2099-01-02T00:00:00+03:00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_invalid_date_range_returns_400(self):
        response = self.client.get(
            reverse(
                "device_metrics_by_device_id_history",
                kwargs={"device_id": self.device.device_id},
            ),
            {
                "start_date": "2026-06-03T00:00:00+03:00",
                "end_date": "2026-06-01T00:00:00+03:00",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("start_date", str(response.data))

    def test_invalid_date_format_returns_400(self):
        response = self.client.get(
            reverse(
                "device_metrics_by_device_id_history",
                kwargs={"device_id": self.device.device_id},
            ),
            {"start_date": "not-a-date"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid datetime", response.data["detail"])

    def test_unsupported_query_param_returns_400(self):
        response = self.client.get(
            reverse(
                "device_metrics_by_device_id_history",
                kwargs={"device_id": self.device.device_id},
            ),
            {"days": 7},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported query parameter", response.data["detail"])

    def test_page_size_max_is_enforced(self):
        response = self.client.get(
            reverse(
                "device_metrics_by_device_id_history",
                kwargs={"device_id": self.device.device_id},
            ),
            {"page_size": 501},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("page_size", response.data)

    def test_hourly_aggregates_bucket_readings(self):
        response = self.client.get(
            reverse(
                "device_metrics_by_device_id_aggregates",
                kwargs={"device_id": self.device.device_id},
            ),
            {
                "start_date": self.start.isoformat(),
                "end_date": (self.start + timedelta(hours=3)).isoformat(),
                "granularity": "hourly",
                "ordering": "timestamp",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["avg_db_level"], 44.0)
        self.assertEqual(response.data["results"][0]["max_db_level"], 50.0)
        self.assertEqual(response.data["results"][0]["reading_count"], 1)


class AIHistoryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.device = Device.objects.create(
            device_id="SEAS-2",
            imei="123456789012347",
            device_name="SAES v1 Naguru",
            phone_number="0700000002",
            version_number="1",
            production_stage="Deployed",
            device_type=Device.DeviceType.MPU,
        )
        self.start = timezone.make_aware(datetime(2026, 6, 12, 0, 0, 0))
        old_env = EnvironmentalParameter.objects.create(
            device=self.device,
            temperature=20.0,
            pressure=868.0,
            humidity=80.0,
            air_quality=70.0,
            power_usage=8.0,
            db_level=50.0,
        )
        new_env = EnvironmentalParameter.objects.create(
            device=self.device,
            temperature=21.0,
            pressure=869.0,
            humidity=81.0,
            air_quality=71.0,
            power_usage=8.1,
            db_level=60.0,
        )
        set_timestamp(old_env, "created_at", self.start - timedelta(days=2))
        set_timestamp(new_env, "created_at", self.start + timedelta(hours=2))

        old_inference = SoundInferenceData.objects.create(
            device=self.device,
            inference_probability=0.1,
            inference_class="traffic",
            inferred_audio_name="old.wav",
        )
        new_inference = SoundInferenceData.objects.create(
            device=self.device,
            inference_probability=0.9,
            inference_class="generator",
            inferred_audio_name="new.wav",
        )
        set_timestamp(old_inference, "created_at", self.start - timedelta(days=2))
        set_timestamp(new_inference, "created_at", self.start + timedelta(hours=3))

    def test_environmental_history_filters_by_device_id_and_date(self):
        response = self.client.get(
            reverse(
                "environmentalparameter-by-device-id-history",
                kwargs={"device_id": self.device.device_id},
            ),
            {
                "start_date": self.start.isoformat(),
                "end_date": (self.start + timedelta(days=1)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["device"]["device_id"], "SEAS-2")
        self.assertEqual(response.data["results"][0]["db_level"], 60.0)
        self.assertEqual(response.data["results"][0]["temperature"], 21.0)

    def test_sound_inference_history_filters_by_device_id_and_date(self):
        response = self.client.get(
            reverse(
                "soundinferencedata-by-device-id-history",
                kwargs={"device_id": self.device.device_id},
            ),
            {
                "start_date": self.start.isoformat(),
                "end_date": (self.start + timedelta(days=1)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["inference_class"], "generator")
        self.assertEqual(response.data["results"][0]["inference_probability"], 0.9)

    def test_latest_ai_endpoints_remain_unchanged(self):
        env_response = self.client.get(
            reverse(
                "environmentalparameter-by-device-id",
                kwargs={"device_id": self.device.device_id},
            )
        )
        inference_response = self.client.get(
            reverse(
                "soundinferencedata-by-device-id",
                kwargs={"device_id": self.device.device_id},
            )
        )

        self.assertEqual(env_response.status_code, 200)
        self.assertNotIn("results", env_response.data)
        self.assertEqual(env_response.data["db_level"], 60.0)
        self.assertEqual(inference_response.status_code, 200)
        self.assertNotIn("results", inference_response.data)
        self.assertEqual(inference_response.data["inference_class"], "generator")


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
            "id,device,temperature,pressure,humidity,air_quality,ram_value,system_temperature,power_usage,db_level,created_at",
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
        self.assertEqual(
            len(content.splitlines()), 11
        )  # (pages 2 and 3 = 10 rows) + 1 header

    def test_export_csv_year(self):
        # Create records for a different year
        from datetime import datetime

        from django.utils import timezone

        param = EnvironmentalParameter.objects.create(
            device=self.device,
            temperature=99.0,
            pressure=999.0,
            humidity=99.0,
            air_quality=9.0,
            ram_value=999.0,
            system_temperature=99.0,
            power_usage=9.0,
        )
        # Set created_at to 2020
        param.created_at = timezone.make_aware(datetime(2020, 5, 1, 12, 0, 0))
        param.save()

        # Get only current year records
        current_year = timezone.now().year
        response = self.client.get(self.url, {"year": current_year})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Should not include the 2020 record
        self.assertNotIn("99.0,999.0,99.0,9.0,999.0,99.0,9.0", content)
        # Should include at least one of the current year records
        self.assertIn(str(current_year), content)

        # Get only 2020 records
        response = self.client.get(self.url, {"year": 2020})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("99.0,999.0,99.0,9.0,999.0,99.0,9.0", content)
