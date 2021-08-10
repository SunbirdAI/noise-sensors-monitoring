from django.forms import ModelForm, ValidationError
from .models import Device


class DeviceForm(ModelForm):
    class Meta:
        model = Device
        exclude = ['id']

    def clean_imei(self, *args, **kwargs):
        imei = self.cleaned_data.get('imei')
        if len(imei) != 15:
            raise ValidationError('IMEI must be 15-digit number')
        return imei

