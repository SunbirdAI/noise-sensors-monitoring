from .views import ReceiveDeviceMetricsViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', ReceiveDeviceMetricsViewSet)
urlpatterns = router.urls
