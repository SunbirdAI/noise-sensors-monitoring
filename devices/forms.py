from django.forms import ModelForm, ValidationError
from .models import Device, Location
import re


class DeviceForm(ModelForm):
    class Meta:
        model = Device
        fields = ['device_id', 'imei', 'device_name', 'phone_number', 'version_number',
                  'production_stage', 'tags', 'metrics_url'] 

    def clean_imei(self, *args, **kwargs):
        imei = self.cleaned_data.get('imei')
        if len(imei) != 15:
            raise ValidationError('IMEI must be 15-digit number')
        return imei

    def clean_phone_number(self, *args, **kwargs):
        # this particular validation is a placeholder and should be updated later
        phone_number = self.cleaned_data.get('phone_number')
        pattern = '^(07)([0-9]{8})$'
        if not re.match(pattern, phone_number):
            raise ValidationError('Please enter a valid phone number')
        return phone_number


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ['latitude', 'longitude', 'city', 'division', 'parish', 'village', 'category']


class DeviceConfigurationForm(ModelForm):
    class Meta:
        model = Device
        fields = ['configured', 'mode', 'dbLevel', 'recLength', 'recInterval', 'uploadAddr']
