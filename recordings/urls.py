from .views import ReceiveAudioViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', ReceiveAudioViewSet)
urlpatterns = router.urls
