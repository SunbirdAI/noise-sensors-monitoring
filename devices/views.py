from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from .models import Device
from django.http import HttpResponseRedirect

from .forms import DeviceForm


class DeviceListView(ListView):
    model = Device
    context_object_name = 'device_list'
    template_name = 'devices/device_list.html'


class DeviceDetailView(DetailView):
    model = Device
    context_object_name = 'device'
    template_name = 'devices/device_detail.html'


class DeviceFormView(FormView):
    template_name = 'devices/create_device.html'
    form_class = DeviceForm
    success_url = '/devices/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
