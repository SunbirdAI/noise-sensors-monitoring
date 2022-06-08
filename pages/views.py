import pytz
from datetime import datetime

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from noise_dashboard.settings import TIME_ZONE
from devices.models import Device
from recordings.models import Recording

class HomePageView(TemplateView):
    template_name = 'home.html'

    def devices_count(self):
        """ Count of all devices """
        return Device.objects.count()

    def deployed_devices_count(self):
        """ 
        Count of all devices with
        production_stage as 'Deployed' 
        """
        return Device.objects.filter(production_stage='Deployed').count()

    def recordings_count(self):
        """ Count of all recordings """
        return Recording.objects.count()

    def recordings_count_today(self):
        """ Count of all recordings """
        timezone = pytz.timezone(TIME_ZONE)
        today = datetime.today()
        today = timezone.localize(today)
        return Recording.objects.filter(
            time_recorded__year=today.year,
            time_recorded__month=today.month,
            time_recorded__day=today.day
        ).count()
