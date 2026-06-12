from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from device_metrics.models import DeviceMetrics, EnvironmentalParameter

from .models import Device


class DeviceTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="lsanyu", email="lsanyu@email.com", password="pass123"
        )
        self.client.force_login(self.user)
        self.metrics_url = "http://localhost:3000/d/Fmi1Q1qGk/sensor-metrics-dashboard?orgId=1&refresh=30s"
        self.device = Device.objects.create(
            device_id="SB1001",
            imei="33414214123",
            device_name="First sensor",
            phone_number="0700443425",
            version_number="1.0.0",
            production_stage="Testing",
            metrics_url=self.metrics_url,
        )

    def test_device_listing(self):
        self.assertEqual(f"{self.device.device_id}", "SB1001")
        self.assertEqual(f"{self.device.imei}", "33414214123"),
        self.assertEqual(f"{self.device.phone_number}", "0700443425")
        self.assertEqual(f"{self.device.production_stage}", "Testing")
        self.assertEqual(f"{self.device.version_number}", "1.0.0")
        self.assertEqual(f"{self.device.metrics_url}", self.metrics_url)

    def test_device_list_view(self):
        response = self.client.get(reverse("device_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SB1001")
        self.assertTemplateUsed(response, "devices/device_list.html")

    def test_device_list_view_shows_health_metrics(self):
        EnvironmentalParameter.objects.create(
            device=self.device,
            temperature=30.29,
            pressure=871.4,
            humidity=52.056,
            air_quality=47.19460416410085,
            ram_value=426,
            system_temperature=54.2,
            power_usage=8.296,
            db_level=62.35,
        )
        DeviceMetrics.objects.create(
            device=self.device,
            sig_strength=26,
            db_level=60.1,
            avg_db_level=59.5,
            max_db_level=68.2,
            no_of_exceedances=0,
            last_rec=1.0,
            last_upl=2.0,
            panel_voltage=5.2,
            battery_voltage=4.1,
            data_balance=120,
        )

        response = self.client.get(reverse("device_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "30.3")
        self.assertContains(response, "871.4")
        self.assertContains(response, "Good&nbsp;(26)")
        self.assertContains(response, "62.4")

    def test_device_list_view_filters_by_status(self):
        maintenance_device = Device.objects.create(
            device_id="SB1002",
            imei="123456789012345",
            device_name="Maintenance sensor",
            phone_number="0700443426",
            version_number="1.0.0",
            production_stage="Maintenance",
            metrics_url=self.metrics_url,
        )

        response = self.client.get(reverse("device_list"), {"status": "issue"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, maintenance_device.device_id)
        self.assertNotContains(response, self.device.device_id)

    def test_device_detail_view(self):
        response = self.client.get(self.device.get_absolute_url())
        no_response = self.client.get("/devices/122143")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "SB1001")
        self.assertTemplateUsed(response, "devices/device_detail.html")

    def test_device_edit_view(self):
        response = self.client.post(
            reverse("edit_device", kwargs={"pk": self.device.id}),
            {
                "device_name": "First sensor - edited",
                "imei": "123456789012345",
                "phone_number": "0771234567",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First sensor - edited")

    def test_device_edit_view_short_phone_no(self):
        response = self.client.post(
            reverse("edit_device", kwargs={"pk": self.device.id}),
            {"phone_number": "077123456"},
        )
        self.assertContains(response, "Please enter a valid phone number")

    def test_device_edit_view_wrong_phone_no(self):
        response = self.client.post(
            reverse("edit_device", kwargs={"pk": self.device.id}),
            {"phone_number": "0990123456"},
        )
        self.assertContains(response, "Please enter a valid phone number")

    def test_device_edit_view_invalid_imei(self):
        response = self.client.post(
            reverse("edit_device", kwargs={"pk": self.device.id}),
            {"imei": "1234567890"},
        )
        self.assertContains(response, "IMEI must be 15-digit number")
