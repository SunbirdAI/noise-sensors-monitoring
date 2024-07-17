from django.test import TestCase

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
