from django.urls import path

from .views import AdvisorInsightView

urlpatterns = [
    path(
        "device/by-device-id/<str:device_id>/insight/",
        AdvisorInsightView.as_view(),
        name="advisor_device_insight",
    ),
]
