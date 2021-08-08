from django.test import TestCase
from django.urls import reverse

from .models import Device


class BookTests(TestCase):

    def setUp(self) -> None:
        self.device = Device.objects.create(
            device_id='SB1001',
            imei='33414214123',
            device_name='First sensor',
            phone_number='0700443425',
            production_stage='Testing'
        )

    def test_device_listing(self):
        self.assertEqual(f'{self.device.device_id}', 'SB1001')
        self.assertEqual(f'{self.device.imei}', '33414214123'),
        self.assertEqual(f'{self.device.phone_number}', '0700443425')
        self.assertEqual(f'{self.device.production_stage}', 'Testing')

    def test_book_list_view(self):
        response = self.client.get(reverse('device_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SB1001')
        self.assertTemplateUsed(response, 'devices/device_list.html')

    def test_book_detail_view(self):
        response = self.client.get(self.device.get_absolute_url())
        no_response = self.client.get('/devices/122143')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, 'SB1001')
        self.assertTemplateUsed(response, 'devices/device_detail.html')
