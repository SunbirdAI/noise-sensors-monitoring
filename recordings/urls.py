from rest_framework.routers import SimpleRouter

from .views import ReceiveAudioViewSet, ReceiveAudioViewSetV2, UpdateAudioViewSet

router = SimpleRouter()
router.register("", ReceiveAudioViewSet)
router.register("test_version", ReceiveAudioViewSetV2)
router.register("update", UpdateAudioViewSet)
urlpatterns = router.urls
