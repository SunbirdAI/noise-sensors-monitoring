from datetime import datetime, timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from devices.models import Device, Location
from device_metrics.history import get_timezone
from device_metrics.models import DeviceMetrics, SoundInferenceData

from .features import build_features


LOC_MEM_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "advisor-tests",
    }
}


def set_timestamp(instance, field_name, value):
    setattr(instance, field_name, value)
    instance.save(update_fields=[field_name])


def create_metric(
    device,
    uploaded_at,
    db_level=50.0,
    avg_db_level=None,
    max_db_level=None,
    no_of_exceedances=1,
):
    metric = DeviceMetrics.objects.create(
        device=device,
        sig_strength=31,
        db_level=db_level,
        avg_db_level=avg_db_level,
        max_db_level=max_db_level,
        no_of_exceedances=no_of_exceedances,
        last_rec=0.0,
        last_upl=0.0,
        panel_voltage=18.0,
        battery_voltage=3.8,
        data_balance=300,
    )
    set_timestamp(metric, "time_uploaded", uploaded_at)
    return metric


def create_device(device_id="SB1006"):
    return Device.objects.create(
        device_id=device_id,
        imei="123456789012345",
        device_name="Naguru Summit View",
        phone_number="0700000000",
        version_number="1",
        production_stage="Deployed",
        device_type=Device.DeviceType.MCU,
    )


def create_location(device):
    return Location.objects.create(
        latitude=0.3476,
        longitude=32.5825,
        city="Kampala",
        division="Nakawa",
        parish="Nakawa",
        village="Kiwatule",
        device=device,
        category=Location.Category.B,
    )


def create_recent_metrics(device, count=20):
    now = timezone.now()
    for index in range(count):
        create_metric(device, now - timedelta(hours=index + 1), db_level=55.0)


@override_settings(SECURE_SSL_REDIRECT=False, CACHES=LOC_MEM_CACHE)
class AdvisorInsightViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()

    @patch("advisor.views.call_openai")
    def test_fresh_cache_hit_returns_ready_without_openai(self, mock_call_openai):
        device = create_device()
        cache.set(
            "advisor:SB1006:en:resident",
            {
                "status": "ready",
                "insight": "Cached insight",
                "generated_at": "2026-07-06T12:00:00+03:00",
                "range": {
                    "start_date": "2026-06-29T12:00:00+03:00",
                    "end_date": "2026-07-06T12:00:00+03:00",
                },
            },
        )

        response = self.client.get(
            reverse("advisor_device_insight", kwargs={"device_id": device.device_id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["device_id"], "SB1006")
        self.assertEqual(response.data["status"], "ready")
        self.assertEqual(response.data["insight"], "Cached insight")
        self.assertTrue(response.data["cached"])
        mock_call_openai.assert_not_called()

    @patch("advisor.views.call_openai", return_value="Generated insight")
    def test_cache_miss_generates_caches_and_returns_ready(self, mock_call_openai):
        device = create_device()
        create_location(device)
        create_recent_metrics(device, 22)

        response = self.client.get(
            reverse("advisor_device_insight", kwargs={"device_id": device.device_id}),
            {"lang": "en", "audience": "official"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ready")
        self.assertEqual(response.data["insight"], "Generated insight")
        self.assertFalse(response.data["cached"])
        self.assertIsNotNone(response.data["generated_at"])
        mock_call_openai.assert_called_once()

        cached = cache.get("advisor:SB1006:en:official")
        self.assertEqual(cached["status"], "ready")
        self.assertEqual(cached["insight"], "Generated insight")

        cached_response = self.client.get(
            reverse("advisor_device_insight", kwargs={"device_id": device.device_id}),
            {"lang": "en", "audience": "official"},
        )
        self.assertTrue(cached_response.data["cached"])
        mock_call_openai.assert_called_once()

    @patch("advisor.views.call_openai")
    def test_invalid_lang_and_audience_return_400(self, mock_call_openai):
        device = create_device()

        lang_response = self.client.get(
            reverse("advisor_device_insight", kwargs={"device_id": device.device_id}),
            {"lang": "fr"},
        )
        audience_response = self.client.get(
            reverse("advisor_device_insight", kwargs={"device_id": device.device_id}),
            {"audience": "planner"},
        )

        self.assertEqual(lang_response.status_code, 400)
        self.assertEqual(audience_response.status_code, 400)
        mock_call_openai.assert_not_called()

    @patch("advisor.views.call_openai")
    def test_nonexistent_device_returns_404_without_openai(self, mock_call_openai):
        response = self.client.get(
            reverse("advisor_device_insight", kwargs={"device_id": "missing"})
        )

        self.assertEqual(response.status_code, 404)
        mock_call_openai.assert_not_called()

    @patch("advisor.views.call_openai")
    def test_low_readings_returns_empty_without_openai(self, mock_call_openai):
        device = create_device()
        create_location(device)
        create_recent_metrics(device, 3)

        response = self.client.get(
            reverse("advisor_device_insight", kwargs={"device_id": device.device_id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "empty")
        self.assertIsNone(response.data["insight"])
        self.assertFalse(response.data["cached"])
        self.assertIsNone(response.data["generated_at"])
        mock_call_openai.assert_not_called()

    @patch("advisor.views.call_openai", return_value=None)
    def test_openai_failure_returns_unavailable_and_null_insight(
        self, mock_call_openai
    ):
        device = create_device()
        create_location(device)
        create_recent_metrics(device, 21)

        response = self.client.get(
            reverse("advisor_device_insight", kwargs={"device_id": device.device_id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "unavailable")
        self.assertIsNone(response.data["insight"])
        self.assertFalse(response.data["cached"])
        mock_call_openai.assert_called_once()


@override_settings(SECURE_SSL_REDIRECT=False, CACHES=LOC_MEM_CACHE)
class AdvisorFeatureTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_features_math_uses_aggregates_and_location_limits(self):
        tz = get_timezone("Africa/Kampala")
        device = create_device()
        create_location(device)
        start = datetime(2026, 6, 1, 0, 0, tzinfo=tz)
        end = start + timedelta(days=7)
        previous_start = start - timedelta(days=7)

        for index in range(10):
            create_metric(device, start + timedelta(hours=index + 1), db_level=40.0)
            create_metric(device, previous_start + timedelta(hours=index + 1), 40.0)
        for index in range(10, 20):
            create_metric(device, start + timedelta(hours=index + 1), db_level=60.0)
            create_metric(device, previous_start + timedelta(hours=index + 1), 40.0)

        SoundInferenceData.objects.create(
            device=device,
            inference_probability=0.95,
            inference_class="Traffic",
            inferred_audio_name="traffic.wav",
        )

        features = build_features(device, start, end, tz)

        self.assertEqual(features["avg_db"], 50.0)
        self.assertEqual(features["peak_db"], 60.0)
        self.assertEqual(features["exceedances"], 20)
        self.assertEqual(features["day_limit"], 50)
        self.assertEqual(features["night_limit"], 35)
        self.assertEqual(features["pct_over_day"], 50.0)
        self.assertEqual(features["pct_over_night"], 100.0)
        self.assertEqual(features["loudest_hour"]["peak_db"], 60.0)
        self.assertEqual(features["loudest_day"]["peak_db"], 60.0)
        self.assertEqual(features["dominant_sound"], "Traffic")
        self.assertEqual(features["readings"], 20)
        self.assertEqual(features["trend_vs_prev"], 10.0)
        self.assertEqual(features["location_label"], "Kiwatule, Nakawa, Kampala")
        self.assertEqual(features["range"]["start_date"], start.isoformat())
        self.assertEqual(features["range"]["end_date"], end.isoformat())

    def test_features_use_null_limits_without_location(self):
        tz = get_timezone("Africa/Kampala")
        device = create_device()
        start = datetime(2026, 6, 1, 0, 0, tzinfo=tz)
        end = start + timedelta(days=7)
        create_metric(device, start + timedelta(hours=1), db_level=60.0)

        features = build_features(device, start, end, tz)

        self.assertIsNone(features["day_limit"])
        self.assertIsNone(features["night_limit"])
        self.assertIsNone(features["pct_over_day"])
        self.assertIsNone(features["pct_over_night"])
        self.assertIsNone(features["location_label"])
