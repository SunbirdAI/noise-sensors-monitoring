from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from .models import DeviceMetrics
from .serializers import (
    DeviceMetricsFullSerializer, DeviceMetricsPartialSerializer
)
from rest_framework import viewsets

from .forms import DeviceMetricsForm


class DeviceMetricsListView(ListView):
    model = DeviceMetrics
    context_object_name = 'device_metrics_list'
    # template_name = 'device_metrics/list.html'

class DeviceMetricsCreateView(CreateView):
    model = DeviceMetrics
    form_class = DeviceMetricsForm

