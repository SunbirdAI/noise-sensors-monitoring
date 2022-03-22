from .views import ReceiveAudioViewSet, UpdateAudioViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('', ReceiveAudioViewSet)
router.register('update', UpdateAudioViewSet)
urlpatterns = router.urls
