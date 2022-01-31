from django.urls import path, include

from .views import ReceiveDeviceMetricsViewSet

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', ReceiveDeviceMetricsViewSet)

urlpatterns = [
    path('', include(router.urls))
]